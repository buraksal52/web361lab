import type { CodeFiles, Language } from './Editor'

function scriptString(value: string) {
  return JSON.stringify(value).replace(/</g, '\\u003c')
}

export function previewDocument(files: CodeFiles, enabledLanguages: Language[]) {
  const html = enabledLanguages.includes('html') ? files.html : ''
  const css = enabledLanguages.includes('css') ? files.css : ''
  const javascript = enabledLanguages.includes('javascript') ? files.javascript : ''
  const policy = "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; form-action 'none'; base-uri 'none'"

  return `<!doctype html><meta http-equiv="Content-Security-Policy" content="${policy}"><script>\n` +
    `document.addEventListener('DOMContentLoaded', () => {\n` +
    `const style = document.createElement('style'); style.textContent = ${scriptString(css)}; document.head.appendChild(style);\n` +
    `const script = document.createElement('script'); script.textContent = ${scriptString(javascript)}; document.body.appendChild(script);\n` +
    `});</script>${html}`
}

type PreviewProps = {
  files: CodeFiles
  enabledLanguages: Language[]
}

export function Preview({ files, enabledLanguages }: PreviewProps) {
  return <iframe title="Canlı önizleme" sandbox="allow-scripts" srcDoc={previewDocument(files, enabledLanguages)} />
}
