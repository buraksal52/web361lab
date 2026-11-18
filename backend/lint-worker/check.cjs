const { HTMLHint, HTMLParser } = require('htmlhint')
const csstree = require('css-tree')
const { Linter } = require('eslint')
const globals = require('globals')
const prettier = require('prettier/standalone')
const htmlPlugin = require('prettier/plugins/html')
const cssPlugin = require('prettier/plugins/postcss')

const messages = {
  'tag-pair': 'Etiketlerin açılış ve kapanışlarını kontrol edin.',
  'id-unique': 'Aynı id değerini birden fazla öğede kullanmayın.',
  'alt-require': 'Görsel için alt açıklaması ekleyin.',
  'doctype-first': 'Belgenin başına HTML doctype bildirimi ekleyin.',
  'tag-no-obsolete': 'Bu eski HTML etiketini kullanmaktan kaçının.',
  'presentational-tag': 'Bu etiketin kullanım amacını gözden geçirin.',
  'attr-no-duplication': 'Aynı özelliği bir öğede bir kez kullanın.',
  'attr-value-double-quotes': 'Özellik değerini çift tırnak içinde yazın.',
  'attr-value-not-empty': 'Özellik değerini boş bırakmayın.',
  'tagname-lowercase': 'Etiket adını küçük harflerle yazın.',
  'attr-lowercase': 'Özellik adını küçük harflerle yazın.',
  'src-not-empty': 'Kaynak adresini boş bırakmayın.',
  'title-require': 'Belgeye bir title öğesi ekleyin.',
  'html-lang-require': 'HTML öğesinde belge dilini belirtin.',
  'css-syntax': 'CSS yazımını ve noktalama işaretlerini kontrol edin.',
  'css-unknown-property': 'CSS özellik adını kontrol edin.',
  'css-invalid-value': 'Bu özellik için kullanılan CSS değerini kontrol edin.',
  eqeqeq: 'Karşılaştırmada === veya !== kullanmayı değerlendirin.',
  'no-unused-vars': 'Tanımlanan değişken kullanılmıyor.',
  'no-undef': 'Kullanılan adın tanımlandığından emin olun.',
  indent: 'Satırın girintisini diğer satırlarla tutarlı hale getirin.',
  indentation: 'Satırın girintisini diğer satırlarla tutarlı hale getirin.',
}

const syntaxMessages = [
  [/Unexpected token/, 'JavaScript yazımında beklenmeyen bir öğe var.'],
  [/Unterminated string/, 'Metin ifadesinin kapanış tırnağını kontrol edin.'],
  [/Unterminated comment/, 'Yorumun kapanış işaretini kontrol edin.'],
  [/Unterminated regular expression/, 'Düzenli ifadenin kapanışını kontrol edin.'],
  [/already been declared/, 'Bu ad aynı kapsamda daha önce tanımlanmış.'],
  [/'return' outside of function/, 'return ifadesini bir fonksiyon içinde kullanın.'],
  [/Unexpected character/, 'JavaScript ifadesindeki beklenmeyen karakteri kontrol edin.'],
  [/Invalid number/, 'Sayı ifadesinin yazımını kontrol edin.'],
]

function issue(language, rule, raw, line, column, severity = 'warning') {
  const syntaxMessage = rule === 'js-syntax' ? syntaxMessages.find(([pattern]) => pattern.test(raw))?.[1] : undefined
  return { language, rule, message: messages[rule] || syntaxMessage || raw, raw_message: raw, line: line || 1, column: column || 1, severity }
}

function neutralizeHtmlDirectives(html) {
  return html.replace(/<!--[\s\S]*?-->/g, comment => comment.replace(/htmlhint/gi, 'htmlh_nt'))
}

HTMLHint.addRule({
  id: 'presentational-tag',
  description: 'Report selected presentation-oriented tags',
  init(parser, reporter) {
    parser.addListener('tagstart', event => {
      if (['i', 'b', 'center', 'font'].includes(event.tagName.toLowerCase())) {
        reporter.warn(`Presentation-oriented tag: ${event.tagName}`, event.line, event.col, this, event.raw)
      }
    })
  },
})

function htmlIssues(html, rules) {
  const map = { html_tag_pair: 'tag-pair', html_id_unique: 'id-unique', html_alt: 'alt-require', html_doctype: 'doctype-first', html_presentational: 'presentational-tag' }
  const selected = Object.fromEntries(Object.entries(map).filter(([key]) => rules.includes(key)).map(([, value]) => [value, true]))
  if (!Object.keys(selected).length) return []
  return HTMLHint.verify(neutralizeHtmlDirectives(html), selected).map(item => issue('html', item.rule.id, item.message, item.line, item.col, item.rule.id === 'tag-pair' ? 'error' : 'warning'))
}

function cssIssues(code, rules, language = 'css', lineOffset = 0, columnOffset = 0) {
  if (!rules.some(rule => ['css_syntax', 'css_unknown_property', 'css_invalid_value'].includes(rule))) return []
  const output = []
  let ast
  try {
    ast = csstree.parse(code, { positions: true, onParseError(error) {
      if (rules.includes('css_syntax')) output.push(issue(language, 'css-syntax', error.message, lineOffset + error.line, error.column + (error.line === 1 ? columnOffset : 0), 'error'))
    } })
  } catch (error) {
    if (rules.includes('css_syntax')) output.push(issue(language, 'css-syntax', error.message, lineOffset + (error.line || 1), (error.column || 1) + ((error.line || 1) === 1 ? columnOffset : 0), 'error'))
    return output
  }
  csstree.walk(ast, node => {
    if (node.type !== 'Declaration' || node.property.startsWith('--')) return
    const result = csstree.lexer.matchProperty(node.property, node.value)
    if (!result.error || /var\(/i.test(csstree.generate(node.value))) return
    const unknown = /^Unknown property/.test(result.error.message)
    if ((unknown && rules.includes('css_unknown_property')) || (!unknown && rules.includes('css_invalid_value'))) {
      output.push(issue(language, unknown ? 'css-unknown-property' : 'css-invalid-value', result.error.message, lineOffset + node.loc.start.line, node.loc.start.column + (node.loc.start.line === 1 ? columnOffset : 0)))
    }
  })
  return output
}

function jsIssues(code, rules, language = 'javascript', lineOffset = 0, isModule = false, columnOffset = 0) {
  const selected = {}
  if (rules.includes('js_eqeqeq')) selected.eqeqeq = 'warn'
  if (rules.includes('js_unused')) selected['no-unused-vars'] = 'warn'
  if (rules.includes('js_undef')) selected['no-undef'] = 'warn'
  if (rules.includes('indentation')) selected.indent = ['warn', indentStyle(code).eslint, { SwitchCase: 1 }]
  if (!Object.keys(selected).length && !rules.includes('js_syntax')) return []
  const findings = new Linter().verify(code, {
    languageOptions: { ecmaVersion: 'latest', sourceType: isModule ? 'module' : 'script', globals: globals.browser },
    linterOptions: { noInlineConfig: true }, rules: selected,
  })
  return findings.filter(item => item.ruleId || (item.fatal && rules.includes('js_syntax'))).map(item => issue(language, item.ruleId || 'js-syntax', item.message, lineOffset + item.line, item.column + (item.line === 1 ? columnOffset : 0), item.fatal ? 'error' : 'warning'))
}

function indentStyle(code) {
  const indentation = code.split(/\r?\n/).find(line => /^[ \t]+\S/.test(line))?.match(/^[ \t]+/)?.[0] || '  '
  return indentation.includes('\t') ? { eslint: 'tab', useTabs: true, tabWidth: 2 } : { eslint: Math.min(indentation.length, 8), useTabs: false, tabWidth: Math.min(indentation.length, 8) }
}

async function indentationIssues(code, language) {
  if (!code.trim()) return []
  const options = language === 'html' ? { parser: 'html', plugins: [htmlPlugin] } : { parser: 'css', plugins: [cssPlugin] }
  try {
    const style = indentStyle(code)
    const formatted = await prettier.format(code, { ...options, useTabs: style.useTabs, tabWidth: style.tabWidth })
    const actual = code.replace(/(?:\r?\n)+$/, '').split(/\r?\n/)
    const expected = formatted.replace(/(?:\r?\n)+$/, '').split(/\r?\n/)
    if (actual.length !== expected.length) return []
    const output = []
    for (let index = 0; index < actual.length; index++) {
      if (actual[index].trim() && actual[index].trim() === expected[index].trim() && actual[index].match(/^\s*/)[0] !== expected[index].match(/^\s*/)[0]) {
        output.push(issue(language, 'indentation', 'Indentation differs from the configured format.', index + 1, 1))
      }
    }
    return output
  } catch { return [] }
}

async function analyze({ code, rules }) {
  const findings = [...htmlIssues(code.html, rules), ...cssIssues(code.css, rules), ...jsIssues(code.javascript, rules)]
  const parser = new HTMLParser()
  const embedded = []
  parser.addListener('cdata', event => embedded.push(event))
  parser.parse(code.html)
  for (const block of embedded) {
    const tag = block.tagName.toLowerCase()
    if (tag === 'style') findings.push(...cssIssues(block.raw, rules, 'html', block.line - 1, block.col - 1))
    if (tag === 'script' && !block.attrs.some(attr => attr.name.toLowerCase() === 'src')) {
      const type = block.attrs.find(attr => attr.name.toLowerCase() === 'type')?.value.toLowerCase() || ''
      if (!type || ['module', 'text/javascript', 'application/javascript'].includes(type)) findings.push(...jsIssues(block.raw, rules, 'html', block.line - 1, type === 'module', block.col - 1))
    }
  }
  if (rules.includes('indentation')) {
    findings.push(...await indentationIssues(code.html, 'html'), ...await indentationIssues(code.css, 'css'))
  }
  return findings
}

let input = ''
process.stdin.setEncoding('utf8')
process.stdin.on('data', chunk => { input += chunk })
process.stdin.on('end', async () => {
  try { process.stdout.write(JSON.stringify(await analyze(JSON.parse(input)))) }
  catch { process.stderr.write('Writing check failed'); process.exitCode = 1 }
})
