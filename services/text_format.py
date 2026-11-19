from string import Formatter
from services.i18n import tr

def validate_template(template: str, names: list[str]) -> None:
    if not template:
        return
    if any(not name for name in names) or len(set(names)) != len(names):
        raise ValueError(tr('Template requires unique, nonempty item names.'))
    try:
        for _, field, spec, conversion in Formatter().parse(template):
            if field is not None and (field not in names or spec or conversion):
                raise ValueError()
    except ValueError as exc:
        raise ValueError(tr('Invalid template field or braces.')) from exc

def render_template(template: str, names: list[str], values: list) -> str:
    validate_template(template, names)
    data = dict(zip(names, values))
    return ''.join(literal + (str(data[field]) if field is not None else '')
                   for literal, field, _, _ in Formatter().parse(template))
