import csv
import io
from services.text_format import render_template

def timestamp(seconds):
    ms = round(seconds * 1000)
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    sec, ms = divmod(ms, 1000)
    return f'{hours:02}:{minutes:02}:{sec:02}.{ms:03}'

def format_row(values, seconds, template='', names=()):
    if template:
        values = [render_template(template, names, values)]
    # Quote fields independently so the requested comma-space separator stays CSV compatible.
    fields = []
    for value in [*values, timestamp(seconds)]:
        value = str(value).replace('\r', '\\r').replace('\n', '\\n')
        stream = io.StringIO(newline='')
        csv.writer(stream, lineterminator='\n').writerow([value])
        fields.append(stream.getvalue().rstrip('\n'))
    return ', '.join(fields)

class OutputWriter:
    def __init__(self, path, overwrite=False, template='', names=()):
        self.template, self.names = template, names
        self.file = open(path, 'w' if overwrite else 'x', encoding='utf-8-sig', newline='')
        self.file.write('')  # TextIOWrapper emits the BOM even for an empty result.
        self.file.flush()

    def write(self, values, seconds):
        row = format_row(values, seconds, self.template, self.names)
        self.file.write(row + '\r\n')
        self.file.flush()
        return row

    def close(self):
        self.file.close()
