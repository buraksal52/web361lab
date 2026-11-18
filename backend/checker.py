from dataclasses import dataclass, field
from html.parser import HTMLParser
from multiprocessing import get_context

MAX_HTML_BYTES = 256 * 1024
CHECK_TIMEOUT_SECONDS = 5
VOID_TAGS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


@dataclass
class Element:
    tag: str
    attrs: dict[str, str]
    parent: 'Element | None' = None
    children: list['Element'] = field(default_factory=list)
    text: list[str] = field(default_factory=list)


class DocumentParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Element('document', {})
        self.stack = [self.root]
        self.elements: list[Element] = []

    def handle_starttag(self, tag, attrs):
        if tag in {'li', 'option', 'p'} and self.stack[-1].tag == tag:
            self.stack.pop()
        element = Element(tag, {key: value or '' for key, value in attrs}, self.stack[-1])
        self.stack[-1].children.append(element)
        self.elements.append(element)
        if tag not in VOID_TAGS:
            self.stack.append(element)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.stack.pop()

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.stack[-1].text.append(data)


def has_text(element: Element) -> bool:
    pending = [element]
    while pending:
        node = pending.pop()
        if any(text.strip() for text in node.text):
            return True
        pending.extend(node.children)
    return False


def ancestors(element: Element):
    current = element.parent
    while current is not None:
        yield current
        current = current.parent


def check_html(html: str, rules: list[dict]) -> list[dict]:
    parser = DocumentParser()
    parser.feed(html)
    parser.close()
    labels = {element.attrs.get('for') for element in parser.elements if element.tag == 'label' and element.attrs.get('for')}
    results = []
    for rule in rules:
        count = 0
        for element in parser.elements:
            if element.tag != rule['tag']:
                continue
            if any(name not in element.attrs or (value and element.attrs[name] != value) for name, value in rule['attrs'].items()):
                continue
            if rule['inside'] and not any(parent.tag == rule['inside'] for parent in ancestors(element)):
                continue
            if rule['non_empty'] and not has_text(element):
                continue
            if rule['label_linked']:
                explicit = bool(element.attrs.get('id') and element.attrs['id'] in labels)
                wrapped = any(parent.tag == 'label' and 'for' not in parent.attrs for parent in ancestors(element))
                if element.attrs.get('type', '').lower() == 'hidden' or not (explicit or wrapped):
                    continue
            count += 1
        results.append({'rule': rule, 'count': count, 'used': count >= rule['min_count']})
    return results


def _worker(sender, html, rules):
    try:
        sender.send(('ok', check_html(html, rules)))
    except Exception:
        sender.send(('error', None))
    finally:
        sender.close()


def run_checker(html: str, rules: list[dict]) -> list[dict]:
    if len(html.encode('utf-8')) > MAX_HTML_BYTES:
        raise ValueError('HTML boyutu kontrol için izin verilen sınırı aşıyor.')
    context = get_context('spawn')
    receiver, sender = context.Pipe(duplex=False)
    process = context.Process(target=_worker, args=(sender, html, rules))
    process.start()
    sender.close()
    try:
        if not receiver.poll(CHECK_TIMEOUT_SECONDS):
            raise TimeoutError('Kontrol süresi aşıldı.')
        status, result = receiver.recv()
        if status != 'ok':
            raise RuntimeError('HTML kontrolü tamamlanamadı.')
        return result
    finally:
        receiver.close()
        if process.is_alive():
            process.terminate()
        process.join()
