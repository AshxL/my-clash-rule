import requests
import re

def fetch_and_convert():
    # 定义源文件地址
    url_clash = "https://raw.githubusercontent.com/Loyalsoldier/clash-rules/release/proxy.txt"
    url_global = "https://yfamilys.com/rule/Global.list"

    # 使用集合(Set)来存储规则，利用其特性自动去重
    rules_set = set()

    print("正在下载 Clash 规则 (File 1)...")
    try:
        resp_clash = requests.get(url_clash, timeout=10)
        resp_clash.raise_for_status()
        
        # 解析文件 1 (Clash yaml 格式)
        for line in resp_clash.text.splitlines():
            line = line.strip()
            # 跳过 payload: 开头或空行
            if not line or line.startswith('payload:'):
                continue
            
            # 处理格式:   - 'example.com' 或 - '+.example.com'
            # 1. 去掉开头的 - 和空格
            # 2. 去掉单引号 ' 或双引号 "
            clean_line = line.lstrip("- ").strip("'\"")
            
            # 3. 处理 Clash 的通配符 "+."
            # Clash 的 "+.baidu.com" 等同于 Surge 的 DOMAIN-SUFFIX,baidu.com
            if clean_line.startswith("+."):
                domain = clean_line[2:] # 去掉前两个字符 +.
            else:
                domain = clean_line

            if domain:
                # 按照文件 2 的格式拼接
                rules_set.add(f"DOMAIN-SUFFIX,{domain}")
                
    except Exception as e:
        print(f"下载或处理 Clash 规则失败: {e}")

    print("正在下载 Global 规则 (File 2)...")
    try:
        resp_global = requests.get(url_global, timeout=10)
        resp_global.raise_for_status()

        # 解析文件 2 (直接合并)
        for line in resp_global.text.splitlines():
            line = line.strip()
            # 跳过注释和空行
            if not line or line.startswith("#"):
                continue
            
            # 文件 2 已经是目标格式，直接加入集合
            # 如果文件 2 包含 DOMAIN,xxx 等其他类型，也会被保留
            rules_set.add(line)

    except Exception as e:
        print(f"下载或处理 Global 规则失败: {e}")

    # 排序并写入文件
    print(f"合并完成，共计 {len(rules_set)} 条规则。正在写入 result.list...")
    
    with open("result.list", "w", encoding="utf-8") as f:
        # 添加一些头部信息（可选）
        f.write("# Auto-generated rule list\n")
        f.write("# Mixed content from Loyalsoldier and yfamilys\n")
        
        # 排序后写入，保持列表整洁
        for rule in sorted(rules_set):
            f.write(rule + "\n")
            
    print("完成！")

if __name__ == "__main__":
    fetch_and_convert()
