import requests
import os

def fetch_and_convert():
    # --- 配置 ---
    url_clash = "https://raw.githubusercontent.com/Loyalsoldier/clash-rules/release/proxy.txt"
    url_global = "https://yfamilys.com/rule/Global.list"
    
    # 本地保底文件名
    local_global_file = "Global.list"

    # 伪装头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # 存储最终规则的集合
    rules_set = set()
    
    # 计数统计
    count_1 = 0
    count_2 = 0

    print("--- 开始执行脚本 --- 222")

    # ==========================================
    # 步骤 1: 处理文件 1 (Clash 规则)
    # ==========================================
    print(f"\n[1/3] 处理 Clash 规则: {url_clash}")
    try:
        resp_clash = requests.get(url_clash, headers=headers, timeout=15)
        resp_clash.raise_for_status()
        
        lines = resp_clash.text.splitlines()
        print(f"-> 下载成功，共 {len(lines)} 行")

        for line in lines:
            line = line.strip()
            if not line or line.startswith('payload:'):
                continue
            
            clean_line = line.lstrip("- ").strip("'\"")
            
            if clean_line.startswith("+."):
                domain = clean_line[2:]
            else:
                domain = clean_line

            if domain:
                final_rule = f"DOMAIN-SUFFIX,{domain}"
                if final_rule not in rules_set:
                    rules_set.add(final_rule)
                    count_1 += 1
                    
    except Exception as e:
        print(f"!!! 错误：文件 1 下载失败: {e}")
        # 文件 1 比较稳定，通常不需要本地备份，如果需要也可以加

    # ==========================================
    # 步骤 2: 处理文件 2 (Global 规则 - 含降级策略)
    # ==========================================
    print(f"\n[2/3] 处理 Global 规则: {url_global}")
    
    global_content = ""
    source_type = "远程下载" # 标记来源

    try:
        # 1. 尝试远程下载
        resp_global = requests.get(url_global, headers=headers, timeout=15)
        resp_global.raise_for_status()
        resp_global.encoding = 'utf-8'
        global_content = resp_global.text
        
        print("-> 远程下载成功！")
        
        # 【自动更新机制】下载成功，顺便把内容写入本地 Global.list，作为下次的最新备份
        try:
            with open(local_global_file, "w", encoding="utf-8") as f:
                f.write(global_content)
            print(f"-> 已更新本地备份文件: {local_global_file}")
        except Exception as write_err:
            print(f"-> 警告：无法写入本地备份 (权限或路径问题): {write_err}")

    except Exception as e:
        # 2. 下载失败，触发降级策略
        print(f"-> 远程下载失败 ({e})")
        print(f"-> 正在尝试读取仓库本地备份: {local_global_file}")
        source_type = "本地备份"
        
        if os.path.exists(local_global_file):
            try:
                with open(local_global_file, "r", encoding="utf-8") as f:
                    global_content = f.read()
                print("-> 本地文件读取成功！使用备份数据。")
            except Exception as read_err:
                print(f"!!! 致命错误：本地文件也无法读取: {read_err}")
        else:
            print(f"!!! 致命错误：本地找不到 {local_global_file}，且远程下载失败。")

    # 解析文件 2 内容 (无论是来自远程还是本地)
    if global_content:
        lines = global_content.splitlines()
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            if line not in rules_set:
                rules_set.add(line)
                count_2 += 1
    else:
        print("-> 警告：文件 2 内容为空，跳过处理。")

    # ==========================================
    # 步骤 3: 写入结果
    # ==========================================
    print(f"\n[3/3] 正在写入结果...")
    print(f"  - 文件 1 贡献: {count_1}")
    print(f"  - 文件 2 贡献: {count_2} (来源: {source_type})")
    print(f"  - 总规则数: {len(rules_set)}")
    
    if len(rules_set) > 0:
        with open("result.list", "w", encoding="utf-8") as f:
            f.write("# Auto-generated rule list\n")
            f.write(f"# File 2 Source: {source_type}\n")
            f.write(f"# Total: {len(rules_set)}\n")
            
            for rule in sorted(rules_set):
                f.write(rule + "\n")
        print("-> result.list 生成完毕！")
    else:
        print("!!! 错误：规则集为空，未生成文件。")

if __name__ == "__main__":
    fetch_and_convert()
