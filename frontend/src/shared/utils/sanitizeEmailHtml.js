const ALLOWED_TAGS = new Set(["P", "DIV", "SPAN", "H1", "H2", "H3", "H4", "H5", "H6", "BR", "HR", "UL", "OL", "LI", "B", "STRONG", "I", "EM", "U", "A", "BLOCKQUOTE", "TABLE", "THEAD", "TBODY", "TFOOT", "TR", "TD", "TH"]);
const DROP_WITH_CONTENT = new Set(["SCRIPT", "STYLE", "IFRAME", "OBJECT", "EMBED", "SVG", "MATH", "FORM", "TEXTAREA", "INPUT", "BUTTON", "VIDEO", "AUDIO", "LINK", "META", "BASE", "FRAME", "APPLET"]);
const SAFE_STYLE = new Set(["color", "background-color", "font-family", "font-size", "font-weight", "text-align", "text-decoration", "margin", "padding", "border", "width", "max-width", "height", "line-height"]);

export default function sanitizeEmailHtml(html = "") {
    if (typeof window === "undefined" || !window.DOMParser) return "";
    const document = new DOMParser().parseFromString(String(html), "text/html");
    const clean = (node) => {
        [...node.childNodes].forEach((child) => {
            if (child.nodeType !== Node.ELEMENT_NODE) return;
            const tag = child.tagName;
            if (DROP_WITH_CONTENT.has(tag)) { child.remove(); return; }
            clean(child);
            if (!ALLOWED_TAGS.has(tag)) { child.replaceWith(...child.childNodes); return; }
            [...child.attributes].forEach(({name, value}) => {
                if (name === "title" && tag !== "A") return child.removeAttribute(name);
                if (name === "href" && tag === "A") {
                    const href = value.trim();
                    if (/^(https?:|mailto:|tel:|#|\/)/i.test(href)) return;
                    child.removeAttribute(name);
                    return;
                }
                if (name === "style") {
                    const declarations = [...child.style].filter(property => SAFE_STYLE.has(property) && !/url\s*\(|expression|javascript:/i.test(child.style.getPropertyValue(property)));
                    const safe = declarations.map(property => `${property}: ${child.style.getPropertyValue(property)}`).join("; ");
                    if (safe) child.setAttribute("style", safe); else child.removeAttribute("style");
                    return;
                }
                if (name !== "colspan" && name !== "rowspan") child.removeAttribute(name);
            });
        });
    };
    clean(document.body);
    return document.body.innerHTML;
}
