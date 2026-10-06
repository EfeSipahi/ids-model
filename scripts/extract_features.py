"""HTTP isteklerinden sabit özellikler çıkarır; model eğitmez.

CSIC mini veri için --encoding latin-1 kullanın. Canlı trafik için varsayılan
UTF-8 politikası ve desteklenen içerik türleri ayrıca doğrulanmalıdır.
"""
import argparse
import codecs
import json
import re
from collections import Counter
from email.message import Message
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlsplit

VERSION = '1.0.0'
BASIC_FEATURES = (
    'path_length', 'query_length', 'body_length', 'query_param_count',
    'body_param_count', 'duplicate_param_count', 'max_value_length',
    'mean_value_length', 'percent_encoding_count', 'percent_encoding_ratio',
    'quote_count', 'angle_bracket_count', 'semicolon_count',
    'control_char_count', 'digit_ratio', 'whitespace_ratio',
)
PATTERN_FEATURES = (
    'sql_keyword_count', 'sql_comment_marker_count', 'path_traversal_count',
    'script_tag_present', 'ssi_marker_present',
)
PERCENT = re.compile(r'%[0-9a-fA-F]{2}')
INVALID_PERCENT = re.compile(r'%(?![0-9a-fA-F]{2})')
SQL = re.compile(r'\b(?:select|union|insert|update|delete|drop|alter|create|where|from)\b', re.I)
COMMENTS = re.compile(r'--|/\*|\*/')
TRAVERSAL = re.compile(r'\.\.[/\\]')
SCRIPT = re.compile(r'<script(?=[\s/>]|$)', re.I)
SSI = re.compile(r'<!--#', re.I)


def parse_form(text, encoding):
    """Ayraçları çözümlemeden önce ayırır, tekrarları ve boş değerleri korur."""
    if INVALID_PERCENT.search(text):
        return None, 'invalid_percent_encoding'
    try:
        pairs = parse_qsl(text, keep_blank_values=True, encoding=encoding,
                          errors='strict', max_num_fields=10000, separator='&')
        return pairs, 'parsed' if text else 'empty'
    except (UnicodeError, ValueError, LookupError):
        return None, 'parse_error'


def parse_request(record, encoding='utf-8'):
    codecs.lookup(encoding)
    target = record.get('request_target')
    if not isinstance(target, str):
        raise ValueError('request_target metin olmalı')
    parts = urlsplit(target)
    path, query = parts.path, parts.query
    headers = record.get('headers', [])
    if not isinstance(headers, list) or any(
        not isinstance(h, (list, tuple)) or len(h) != 2
        or not all(isinstance(v, str) for v in h) for h in headers
    ):
        raise ValueError('headers ad/değer çiftlerinden oluşan liste olmalı')
    types = [v for k, v in headers if k.lower() == 'content-type']
    msg = Message()
    if types:
        msg['Content-Type'] = types[0]
    media_type = msg.get_content_type().lower() if types else None
    body_encoding = msg.get_param('charset') or encoding
    body = record.get('body')
    if body is not None and not isinstance(body, str):
        raise ValueError('body metin veya null olmalı')
    qparams, qstatus = parse_form(query, encoding)
    # Eksik kayıt, gerçekten boş body ile aynı değildir.
    if body is None or record.get('body_recorded') is False:
        bparams, bstatus = None, 'missing'
    elif len(types) > 1:
        bparams, bstatus = None, 'ambiguous_content_type'
    elif body == '':
        bparams, bstatus = [], 'empty'
    elif media_type == 'application/x-www-form-urlencoded':
        bparams, bstatus = parse_form(body, body_encoding)
    else:
        bparams, bstatus = None, 'unsupported'
    if INVALID_PERCENT.search(path):
        decoded_path, pstatus = None, 'invalid_percent_encoding'
    else:
        try:
            # URL yolundaki + işareti boşluğa dönüşmez.
            decoded_path = unquote(path, encoding=encoding, errors='strict')
            pstatus = 'parsed'
        except UnicodeError:
            decoded_path, pstatus = None, 'parse_error'
    return dict(path=path, query=query, body=body, query_params=qparams,
                body_params=bparams, decoded_path=decoded_path,
                status=dict(query=qstatus, body=bstatus, path=pstatus,
                            content_type=media_type, body_encoding=body_encoding))


def extract_features(record, encoding='utf-8'):
    """Etiket, kimlik ve kaynak dosya adını okumadan özellik hesaplar."""
    p = parse_request(record, encoding)
    f = {name: None for name in BASIC_FEATURES + PATTERN_FEATURES}
    body = p['body']
    body_known = p['status']['body'] != 'missing'
    f.update(path_length=len(p['path']), query_length=len(p['query']),
             body_length=len(body) if body_known else None,
             query_param_count=len(p['query_params']) if p['query_params'] is not None else None,
             body_param_count=len(p['body_params']) if p['body_params'] is not None else None)
    if body_known:
        count = sum(len(PERCENT.findall(t)) for t in (p['query'], body))
        length = len(p['query']) + len(body)
        f['percent_encoding_count'] = count
        f['percent_encoding_ratio'] = 3 * count / length if length else 0.0
    if p['query_params'] is not None and p['body_params'] is not None:
        groups = (p['query_params'], p['body_params'])
        values = [v for pairs in groups for _, v in pairs]
        total = sum(map(len, values))
        f.update(
            duplicate_param_count=sum(len(pairs)-len({k for k, _ in pairs}) for pairs in groups),
            max_value_length=max(map(len, values), default=0),
            mean_value_length=total/len(values) if values else 0.0,
            quote_count=sum(v.count("'")+v.count('"') for v in values),
            angle_bracket_count=sum(v.count('<')+v.count('>') for v in values),
            semicolon_count=sum(v.count(';') for v in values),
            control_char_count=sum(ord(c)<32 or ord(c)==127 for v in values for c in v),
            digit_ratio=sum(c in '0123456789' for v in values for c in v)/total if total else 0.0,
            whitespace_ratio=sum(c.isspace() for v in values for c in v)/total if total else 0.0,
        )
        if p['decoded_path'] is not None:
            # Parçalar birbirine yapıştırılmaz; sınırda sahte örüntü oluşmaz.
            texts = [p['decoded_path']] + values
            f.update(sql_keyword_count=sum(len(SQL.findall(t)) for t in texts),
                     sql_comment_marker_count=sum(len(COMMENTS.findall(t)) for t in texts),
                     path_traversal_count=sum(len(TRAVERSAL.findall(t)) for t in texts),
                     script_tag_present=int(any(SCRIPT.search(t) for t in texts)),
                     ssi_marker_present=int(any(SSI.search(t) for t in texts)))
    return {'features': f, 'parse_status': p['status']}


def build_feature_table(input_path, output_dir, encoding='utf-8'):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    names = ('features.jsonl', 'feature_report.json')
    if any((output_dir / n).exists() for n in names):
        raise FileExistsError('Çıktı zaten var; yeni bir --output-dir seçin.')
    rows = []
    for line_no, line in enumerate(Path(input_path).read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        record = json.loads(line)
        try:
            result = extract_features(record, encoding)
        except ValueError as e:
            raise ValueError(f'Satır {line_no}: {e}') from e
        rows.append(dict(sample_id=record.get('sample_id', str(line_no)),
                         content_group=record.get('content_group'), label=record.get('label'),
                         **result))
    assert rows, 'Girdi dosyasında kayıt yok'
    report = dict(extractor_version=VERSION, encoding=encoding, records=len(rows),
                  basic_features=list(BASIC_FEATURES), pattern_features=list(PATTERN_FEATURES),
                  labels=dict(Counter(str(r['label']) for r in rows)),
                  parse_status={section: dict(Counter(r['parse_status'][section] for r in rows))
                                for section in ('query','body','path')},
                  missing_values={k: sum(r['features'][k] is None for r in rows)
                                  for k in BASIC_FEATURES + PATTERN_FEATURES},
                  constant_features=[k for k in BASIC_FEATURES + PATTERN_FEATURES
                                     if len({r['features'][k] for r in rows}) == 1],
                  notes=['No model trained; no split or imputation performed.',
                         'Only the features object is an ML input; labels and metadata are separate.',
                         'Lengths are stored-string character counts, not wire byte lengths.',
                         'Query uses form semantics. Only form-urlencoded nonempty bodies supported.',
                         'Headers select the parser; header content and parameter names are not scanned.',
                         'Patterns are literal indicators, not a complete attack detector.'])
    with (output_dir / names[0]).open('w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=True, allow_nan=False)+'\n')
    (output_dir/names[1]).write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--encoding', default='utf-8')
    args = parser.parse_args()
    print(json.dumps(build_feature_table(args.input, args.output_dir, args.encoding), indent=2))
