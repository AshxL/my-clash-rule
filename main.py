import requests
import re

def fetch_and_convert():
    # 定义源文件地址
    url_clash = "https://raw.githubusercontent.com/Loyalsoldier/clash-rules/release/proxy.txt"
    url_global = "https://yfamilys.com/rule/Global.list"

    # 伪装成浏览器的 User-Agent，防止被服务器拦截
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "max-age=0",
        "if-none-match": "W/\"82592ade4548f89e14022b09af3557a3\"",
        "priority": "u=0, i",
        "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "cross-site",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
    }

    # 使用集合(Set)来存储规则，利用其特性自动去重
    rules_set = set()
    
    # 计数器
    count_1 = 0
    count_2 = 0

    print("--- 开始运行 ---")

    # ---------------------------
    # 处理文件 1 (Clash)
    # ---------------------------
    print(f"正在下载 Clash 规则: {url_clash}")
    try:
        resp_clash = requests.get(url_clash, headers=headers, timeout=15)
        resp_clash.raise_for_status()
        resp_clash.encoding = 'utf-8' # 强制编码
        
        lines = resp_clash.text.splitlines()
        print(f"文件 1 下载成功，原始行数: {len(lines)}")

        for line in lines:
            line = line.strip()
            if not line or line.startswith('payload:'):
                continue
            
            # 格式处理: - 'xxx' 或 - "+.xxx"
            clean_line = line.lstrip("- ").strip("'\"")
            
            # 处理 Clash 通配符 "+."
            if clean_line.startswith("+."):
                domain = clean_line[2:]
            else:
                domain = clean_line

            if domain:
                # 转换为 DOMAIN-SUFFIX 格式
                final_rule = f"DOMAIN-SUFFIX,{domain}"
                if final_rule not in rules_set:
                    rules_set.add(final_rule)
                    count_1 += 1
                
    except Exception as e:
        print(f"!!! 错误：处理 Clash 规则失败: {e}")

    # ---------------------------
    # 处理文件 2 (Global)
    # ---------------------------
    print(f"\n正在下载 Global 规则: {url_global}")
    try:
        resp_global = requests.get(url_global, headers=headers, timeout=15)
        resp_global.raise_for_status()
        resp_global.encoding = 'utf-8'
        
        lines = resp_global.text.splitlines()
        print(f"文件 2 下载成功，原始行数: {len(lines)}")

        for line in lines:
            line = line.strip()
            # 跳过注释和空行
            if not line or line.startswith("#"):
                continue
            
            # 文件 2 已经是目标格式，直接添加
            if line not in rules_set:
                rules_set.add(line)
                count_2 += 1

    except Exception as e:
        print(f"!!! 错误：处理 Global 规则失败: {e}")

    # ---------------------------
    # 输出结果
    # ---------------------------
    print(f"\n--- 统计 ---")
    print(f"文件 1 有效规则数: {count_1}")
    print(f"文件 2 有效规则数: {count_2} (新增且不重复)")
    print(f"最终合并规则总数: {len(rules_set)}")
    
    if len(rules_set) == 0:
        print("!!! 警告：没有获取到任何规则，请检查网络或源地址。")
    else:
        print("正在写入 result.list...")
        with open("result.list", "w", encoding="utf-8") as f:
            f.write("# Auto-generated rule list\n")
            f.write(f"# Source 1: {url_clash}\n")
            f.write(f"# Source 2: {url_global}\n")
            f.write(f"# Total rules: {len(rules_set)}\n")
            
            # 排序后写入
            for rule in sorted(rules_set):
                f.write(rule + "\n")
        print("写入完成！")

if __name__ == "__main__":
    fetch_and_convert()
