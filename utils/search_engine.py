import argparse
from utils.user_manager import get_user_paths
from telegram_interface.auth import get_admin_id

def search_history(query, user_id):
    results = []
    paths = get_user_paths(user_id)
    history_file = paths["history"]
    
    if not os.path.exists(history_file):
        return results
    
    with open(history_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    entries = content.split("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    for entry in entries:
        if not entry.strip(): continue
        if query.lower() in entry.lower():
            meta = {}
            time_match = re.search(r"TIME:\s*(.*?)\n", entry)
            skill_match = re.search(r"SKILL:\s*(.*?)\n", entry)
            role_match = re.search(r"ROLE:\s*(.*?)\n", entry)
            
            if time_match: meta['time'] = time_match.group(1).strip()
            if skill_match: meta['skill'] = skill_match.group(1).strip()
            if role_match: meta['role'] = role_match.group(1).strip()
            
            results.append({
                "type": "history",
                "source": "Your Private Conversation History",
                "meta": meta,
                "content": entry.split("────────────────────────────────────────")[-1].strip()
            })
    return results

def search_workspaces(query, user_id):
    results = []
    paths = get_user_paths(user_id)
    workspace_dir = paths["workspace"]
    is_admin = (user_id == get_admin_id())
    
    if not os.path.exists(workspace_dir):
        return results
    
    exts = ('.txt', '.md', '.py', '.js', '.html', '.css', '.skill', '.json')
    
    for root, dirs, files in os.walk(workspace_dir):
        for file in files:
            if file.endswith(exts):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if query.lower() in content.lower():
                            rel_path = os.path.relpath(path, workspace_dir)
                            # PRIVACY: Redact full system paths for non-admin users
                            source_label = f"File: {rel_path}" if is_admin else f"Private Document: {file}"
                            results.append({
                                "type": "workspace",
                                "source": source_label,
                                "content": f"Match found in your isolated data."
                            })
                except: continue
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="*")
    parser.add_argument("--user_id", type=int, required=True)
    args = parser.parse_args()
    
    q = " ".join(args.query)
    user_id = args.user_id
    
    history_res = search_history(q, user_id)
    workspace_res = search_workspaces(q, user_id)
    all_results = history_res + workspace_res
    
    if not all_results:
        print(f"No results found for '{q}'.")
    else:
        for res in all_results:
            print(f"\n[SOURCE: {res['source']}]")
            if res['type'] == 'history':
                print(f"TIME: {res['meta'].get('time', 'N/A')} | SKILL: {res['meta'].get('skill', 'N/A')}")
            print(f"CONTENT: {res['content'][:300]}...")
            print("-" * 20)
