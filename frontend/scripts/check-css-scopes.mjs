import fs from 'node:fs';
import path from 'node:path';
import postcss from 'postcss';

const featuresRoot = path.resolve('src/features');
const appSource = fs.readFileSync(path.resolve('src/app/App.jsx'), 'utf8');
const routeScopes = new Set(
  [...appSource.matchAll(/scopedPage\(["']([^"']+)["']/g)].map((match) => match[1]),
);
const errors = [];

function cssFiles(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const entryPath = path.join(directory, entry.name);
    if (entry.isDirectory()) return cssFiles(entryPath);
    return entry.isFile() && entry.name.endsWith('.css') ? [entryPath] : [];
  });
}

function splitSelectors(value) {
  const selectors = [];
  let start = 0;
  let parentheses = 0;
  let brackets = 0;
  let quote = null;
  let escaped = false;

  for (let index = 0; index < value.length; index += 1) {
    const character = value[index];
    if (escaped) { escaped = false; continue; }
    if (character === '\\') { escaped = true; continue; }
    if (quote) { if (character === quote) quote = null; continue; }
    if (character === '"' || character === "'") { quote = character; continue; }
    if (character === '(') parentheses += 1;
    else if (character === ')') parentheses -= 1;
    else if (character === '[') brackets += 1;
    else if (character === ']') brackets -= 1;
    else if (character === ',' && parentheses === 0 && brackets === 0) {
      selectors.push(value.slice(start, index).trim());
      start = index + 1;
    }
  }
  selectors.push(value.slice(start).trim());
  return selectors;
}

for (const file of cssFiles(featuresRoot)) {
  const relativePath = path.relative(path.resolve('.'), file);
  const source = fs.readFileSync(file, 'utf8');
  const marker = source.match(/Styles scoped to route wrapper \.ui-page-scope--([\w-]+)/);
  if (!marker) {
    errors.push(`${relativePath}: missing route-scope marker`);
    continue;
  }

  const scope = marker[1];
  const prefix = `:where(.ui-page-scope--${scope})`;
  if (!routeScopes.has(scope)) {
    errors.push(`${relativePath}: scope "${scope}" is not declared by a route in src/app/App.jsx`);
  }

  const stylesheet = postcss.parse(source, { from: file });
  const inspect = (nodes, insideKeyframes = false) => {
    nodes.forEach((node) => {
      if (node.type === 'atrule') {
        const isKeyframes = /(?:^|-)(?:webkit-)?keyframes$/i.test(node.name);
        if (node.nodes && !isKeyframes) inspect(node.nodes, insideKeyframes);
      } else if (node.type === 'rule' && !insideKeyframes) {
        for (const selector of splitSelectors(node.selector)) {
          if (!selector.startsWith(prefix)) {
            errors.push(`${relativePath}:${node.source.start.line}: selector is outside ${prefix}: ${selector}`);
          }
        }
      }
    });
  };
  inspect(stylesheet.nodes);
}

if (errors.length) {
  console.error(`CSS route isolation failed (${errors.length} issue${errors.length === 1 ? '' : 's'}):`);
  errors.forEach((error) => console.error(`- ${error}`));
  process.exitCode = 1;
} else {
  console.log(`CSS route isolation passed for ${cssFiles(featuresRoot).length} feature stylesheets.`);
}
