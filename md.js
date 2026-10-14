/* md.js — minimal Markdown renderer (no dependencies) for README/RESULTS pages.
   Supports: headings, hr, fenced code, inline code, bold, italic, links, images,
   ordered/unordered lists, blockquotes, pipe tables. Rewrites .md links to the
   pretty HTML pages. Usage: set window.MD_URL then include this script. */
(function () {
  'use strict';

  function esc(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function inline(s) {
    s = esc(s);
    var tokens = [];
    // protect inline code spans from other transforms
    s = s.replace(/`([^`]+)`/g, function (_, code) {
      tokens.push('<code>' + code + '</code>');
      return '\u0000' + (tokens.length - 1) + '\u0000';
    });
    // images
    s = s.replace(/!\[([^\]]*)\]\(([^)\s]+)\)/g, '<img src="$2" alt="$1">');
    // links (rewrite .md links to pretty pages)
    s = s.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, function (_, txt, href) {
      var h = href;
      if (/^(\.\/)?README\.md$/i.test(h)) h = 'readme.html';
      else if (/(^|\/)RESULTS\.md$/i.test(h)) h = 'results.html';
      return '<a href="' + h + '">' + txt + '</a>';
    });
    // bold then italic
    s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    s = s.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    // restore code tokens
    s = s.replace(/\u0000(\d+)\u0000/g, function (_, i) { return tokens[+i]; });
    return s;
  }

  function isTableRow(l) { return /^\s*\|.*\|\s*$/.test(l); }
  function isTableSep(l) { return /^\s*\|[\s:|-]+\|\s*$/.test(l); }
  function cells(l) {
    // protect escaped pipes (\|) so they don't split cells, then restore as literal |
    var parts = l.trim().replace(/^\|/, '').replace(/\|$/, '')
      .replace(/\\\|/g, '\u0001').split('|')
      .map(function (c) { return c.trim().replace(/\u0001/g, '|'); });
    return parts;
  }

  function renderTable(rows) {
    if (rows.length < 2 || !isTableSep(rows[1])) return null;
    var head = cells(rows[0]);
    var body = rows.slice(2).filter(function (r) { return !isTableSep(r); });
    var h = '<table><thead><tr>' + head.map(function (c) { return '<th>' + inline(c) + '</th>'; }).join('') + '</tr></thead><tbody>';
    body.forEach(function (r) {
      h += '<tr>' + cells(r).map(function (c) { return '<td>' + inline(c) + '</td>'; }).join('') + '</tr>';
    });
    return h + '</tbody></table>';
  }

  function renderMarkdown(md) {
    var lines = md.replace(/\r\n/g, '\n').split('\n');
    var out = [], i = 0;
    while (i < lines.length) {
      var line = lines[i];
      // fenced code
      if (/^```/.test(line)) {
        var buf = []; i++;
        while (i < lines.length && !/^```/.test(lines[i])) { buf.push(lines[i]); i++; }
        i++;
        out.push('<pre><code>' + esc(buf.join('\n')) + '</code></pre>');
        continue;
      }
      // heading
      var h = line.match(/^(#{1,6})\s+(.*)$/);
      if (h) { var lvl = h[1].length; out.push('<h' + lvl + '>' + inline(h[2]) + '</h' + lvl + '>'); i++; continue; }
      // horizontal rule
      if (/^\s*(-{3,}|\*{3,})\s*$/.test(line)) { out.push('<hr>'); i++; continue; }
      // table
      if (isTableRow(line)) {
        var trows = [];
        while (i < lines.length && isTableRow(lines[i])) { trows.push(lines[i]); i++; }
        var tbl = renderTable(trows);
        out.push(tbl || '<p>' + inline(trows.join(' ')) + '</p>');
        continue;
      }
      // blockquote
      if (/^\s*>\s?/.test(line)) {
        var q = [];
        while (i < lines.length && /^\s*>\s?/.test(lines[i])) { q.push(lines[i].replace(/^\s*>\s?/, '')); i++; }
        out.push('<blockquote>' + inline(q.join(' ')) + '</blockquote>');
        continue;
      }
      // lists
      if (/^\s*[-*]\s+/.test(line) || /^\s*\d+\.\s+/.test(line)) {
        var ordered = /^\s*\d+\.\s+/.test(line);
        var items = [];
        while (i < lines.length) {
          var m = lines[i].match(/^\s*(?:[-*]|\d+\.)\s+(.*)$/);
          if (m) { items.push(m[1]); i++; }
          else if (lines[i].trim() && items.length && /^\s+/.test(lines[i])) { items[items.length - 1] += ' ' + lines[i].trim(); i++; }
          else break;
        }
        var tag = ordered ? 'ol' : 'ul';
        out.push('<' + tag + '>' + items.map(function (it) { return '<li>' + inline(it) + '</li>'; }).join('') + '</' + tag + '>');
        continue;
      }
      // blank
      if (!line.trim()) { i++; continue; }
      // paragraph (collect until blank or block start)
      var p = [line]; i++;
      while (i < lines.length && lines[i].trim() &&
             !/^(#{1,6}\s|```|\s*[-*]\s|\s*\d+\.\s|\s*>)/.test(lines[i]) &&
             !isTableRow(lines[i]) && !/^\s*(-{3,}|\*{3,})\s*$/.test(lines[i])) {
        p.push(lines[i]); i++;
      }
      out.push('<p>' + inline(p.join(' ')) + '</p>');
    }
    return out.join('\n');
  }

  function load() {
    var el = document.getElementById('doc');
    if (!el) return;
    fetch(window.MD_URL)
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.text(); })
      .then(function (md) { el.innerHTML = renderMarkdown(md); document.title += ''; })
      .catch(function (e) {
        el.innerHTML = '<p class="doc-error">Could not load ' + window.MD_URL + ' (' + e.message +
          '). The raw file is available <a href="' + window.MD_URL + '">here</a>.</p>';
      });
  }

  // expose for tests
  window.__md = { renderMarkdown: renderMarkdown, inline: inline };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load);
  else load();
})();
