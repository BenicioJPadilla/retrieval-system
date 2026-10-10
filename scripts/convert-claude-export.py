#!/usr/bin/env python3
"""Convert a claude.ai webapp + Claude Design export JSON into vault markdown under vault/sources/.
Usage: python3 scripts/convert-claude-export.py <file.json>
  <file.json> is either conversations.json from the official claude.ai export zip (a list of conversations),
  or a combined {"webapp": {"convs": [...], "projects": [...]}, "design": {"projects": [...]}} file.
Strings matching common API key patterns are redacted."""
import json, os, re, sys, datetime
VAULT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vault", "sources")
KEY_RE = re.compile(r"(sk-ant-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|eyJ[A-Za-z0-9_-]{30,}\.[A-Za-z0-9_-]{30,}\.[A-Za-z0-9_-]{10,}|xox[abp]-[A-Za-z0-9-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----)")
def redact(s): return KEY_RE.sub("[REDACTED-KEY]", s or "")
def slug(s, n=70):
    s = re.sub(r"[^A-Za-z0-9]+", "-", s or "untitled").strip("-").lower()
    return (s[:n] or "untitled").strip("-")
def yaml_str(s): return json.dumps(s or "")
def day(ts): return (ts or "")[:10]
def block_text(block):
    t = block.get("type")
    if t == "text": return block.get("text", "")
    if t == "tool_use":
        name = block.get("name", "tool"); inp = block.get("input", {}) or {}
        if name == "artifacts" and inp.get("content"):
            return f"\n**[artifact: {inp.get('title','')} ({inp.get('type','')})]**\n\n```\n{inp['content'][:12000]}\n```\n"
        if name in ("web_search", "web_fetch"): return f"*[{name}: {inp.get('query') or inp.get('url','')}]*"
        s = json.dumps(inp)[:600]
        return f"*[tool {name}: {s}]*"
    if t == "tool_result":
        c = block.get("content")
        if isinstance(c, list):
            txt = "\n".join(x.get("text","") for x in c if isinstance(x, dict) and x.get("type")=="text")
            return ("*[tool result]* " + txt[:1500]) if txt.strip() else ""
        return ""
    return ""

def convert_webapp(exp):
    projects = {p["uuid"]: p for p in (exp.get("projects") or [])}
    n = 0
    for conv in exp.get("convs", []):
        if not isinstance(conv, dict) or "uuid" not in conv: continue
        proj = projects.get(conv.get("project_uuid") or "", None)
        pname = proj["name"] if proj else "no-project"
        d = os.path.join(VAULT, "claude-webapp", slug(pname, 50)); os.makedirs(d, exist_ok=True)
        name = conv.get("name") or "Untitled"
        fn = f"{day(conv.get('created_at'))}-{slug(name)}.md"
        msgs = conv.get("chat_messages") or []
        lines = ["---", f"title: {yaml_str(name)}", "type: chat", "source: claude.ai web chat",
                 f"source_url: https://claude.ai/chat/{conv['uuid']}", f"project: {yaml_str(pname)}",
                 f"model: {yaml_str(conv.get('model') or '')}", f"created: {day(conv.get('created_at'))}",
                 f"updated: {day(conv.get('updated_at'))}", f"messages: {len(msgs)}",
                 "tags: [claude-webapp, chat" + (", " + slug(pname, 30) if proj else "") + "]", "---", ""]
        if conv.get("summary"): lines += ["> " + redact(conv["summary"]).replace("\n", " "), ""]
        for m in msgs:
            role = "Human" if m.get("sender") == "human" else "Assistant"
            lines.append(f"## {role} · {day(m.get('created_at'))}")
            for a in m.get("attachments") or []:
                ec = a.get("extracted_content")
                if ec: lines += [f"**[attachment: {a.get('file_name','')}]**", "", "```", redact(ec[:15000]), "```", ""]
                else: lines.append(f"*[attachment: {a.get('file_name','')}]*")
            for f in m.get("files") or []: lines.append(f"*[file: {f.get('file_name','')}]*")
            for f in m.get("files_v2") or []: lines.append(f"*[file: {f.get('file_name','')}]*")
            body = "\n\n".join(t for t in (block_text(b) for b in (m.get("content") or [])) if t)
            if not body and m.get("text"): body = m["text"]
            lines += [redact(body), ""]
        with open(os.path.join(d, fn), "w") as f: f.write("\n".join(lines))
        n += 1
    # project instructions + docs
    for p in exp.get("projects") or []:
        d = os.path.join(VAULT, "claude-webapp", slug(p["name"], 50)); os.makedirs(d, exist_ok=True)
        lines = ["---", f"title: {yaml_str('Claude project: ' + p['name'])}", "type: project-context", "source: claude.ai project",
                 f"source_url: https://claude.ai/project/{p['uuid']}", f"updated: {day(p.get('updated_at'))}", "tags: [claude-webapp, project]", "---", "",
                 f"# {p['name']}", "", p.get("description") or "", "", "## Instructions", "", redact(p.get("prompt_template") or "(none)"), ""]
        for doc in p.get("_docs") or []:
            lines += [f"## Knowledge file: {doc.get('file_name','')}", "", "```", redact((doc.get('content') or '')[:40000]), "```", ""]
        if p.get("_memory"): lines += ["## Project memory", "", redact(str(p["_memory"])[:20000]), ""]
        with open(os.path.join(d, "_project.md"), "w") as f: f.write("\n".join(lines))
    return n

def convert_design(des):
    n = 0
    for p in des.get("projects", []):
        d = os.path.join(VAULT, "claude-design", slug(p["name"], 50)); os.makedirs(d, exist_ok=True)
        data = p.get("data") or {}
        chats = list((data.get("chats") or {}).values())
        for c in chats:
            title = c.get("title") or "Untitled"
            lines = ["---", f"title: {yaml_str(p['name'] + ' - ' + title)}", "type: design-chat", "source: Claude Design chat",
                     f"source_url: https://claude.ai/design/p/{p['projectId']}", f"project: {yaml_str(p['name'])}",
                     f"created: {day(c.get('created'))}", f"updated: {day(c.get('lastOpened'))}", f"messages: {len(c.get('messages') or [])}",
                     "tags: [claude-design, chat]", "---", ""]
            for m in c.get("messages") or []:
                role = (m.get("role") or "?").capitalize()
                lines.append(f"## {role} · {day(m.get('timestamp'))}")
                for a in m.get("attachments") or []:
                    if a.get("content"): lines += [f"**[attachment: {a.get('name') or a.get('type','')}]**", "", "```", redact(a['content'][:15000]), "```", ""]
                    else: lines.append(f"*[attachment: {a.get('name') or a.get('type','')}]*")
                cont = m.get("content")
                if isinstance(cont, list):
                    cont = "\n\n".join((x.get("text") or x.get("content") or "") if isinstance(x, dict) else str(x) for x in cont)
                lines += [redact(str(cont or "")), ""]
            with open(os.path.join(d, f"chat-{day(c.get('created'))}-{slug(title)}.md"), "w") as f: f.write("\n".join(lines))
            n += 1
        for fobj in p.get("files") or []:
            path = fobj["path"]; content = fobj.get("content") or ""
            if path.startswith("."): continue
            text = content
            if path.lower().endswith((".html", ".htm")):
                text = re.sub(r"<(script|style)[^>]*>[\s\S]*?</\1>", "", content)
                text = re.sub(r"<[^>]+>", " ", text); text = re.sub(r"[ \t]+", " ", text); text = re.sub(r"\n\s*\n+", "\n\n", text).strip()
            lines = ["---", f"title: {yaml_str(p['name'] + ' - file: ' + path)}", "type: design-file", "source: Claude Design project file",
                     f"source_url: https://claude.ai/design/p/{p['projectId']}?file={path}", f"project: {yaml_str(p['name'])}",
                     f"updated: {day(fobj.get('updatedAt'))}", "tags: [claude-design, file]", "---", "", redact(text[:60000])]
            with open(os.path.join(d, f"file-{slug(path, 80)}.md"), "w") as f: f.write("\n".join(lines))
        # project index
        lines = ["---", f"title: {yaml_str('Claude Design project: ' + p['name'])}", "type: design-project", f"source_url: https://claude.ai/design/p/{p['projectId']}",
                 f"created: {day(p.get('createdAt'))}", f"updated: {day(p.get('updatedAt'))}", "tags: [claude-design, project]", "---", "", f"# {p['name']}", "",
                 f"Chats: {len(chats)} · Files: {len(p.get('files') or [])}", ""]
        for c in chats: lines.append(f"- chat: {c.get('title')} ({len(c.get('messages') or [])} msgs, {day(c.get('created'))})")
        for fobj in p.get("files") or []: lines.append(f"- file: {fobj['path']} ({fobj.get('size')} bytes)")
        with open(os.path.join(d, "_project.md"), "w") as f: f.write("\n".join(lines))
    return n

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: convert-claude-export.py <conversations.json | combined.json>")
    src = sys.argv[1]
    with open(src) as f: data = json.load(f)
    if isinstance(data, list):  # conversations.json from the official claude.ai export zip
        data = {"webapp": {"convs": data, "projects": []}}
    nw = convert_webapp(data["webapp"]) if data.get("webapp") else 0
    nd = convert_design(data["design"]) if data.get("design") else 0
    print(f"webapp chats: {nw}, design chats: {nd}")
