# fix_encoding_final.py
def fix_encoding():
    # 先用错误编码（可能是当前系统编码）读取
    try:
        with open('agent/tools.py', 'rb') as f:
            raw_bytes = f.read()
        
        # 尝试用不同编码解码
        encodings_to_try = ['gbk', 'gb2312', 'gb18030', 'latin-1', 'utf-8']
        
        for encoding in encodings_to_try:
            try:
                content = raw_bytes.decode(encoding)
                # 检查是否包含正常的中文
                if '宪法' in content or '测试' in content:
                    print(f"✅ 找到正确编码: {encoding}")
                    
                    # 用UTF-8重新保存
                    with open('agent/tools.py', 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print("✅ 已用UTF-8重新保存文件")
                    
                    # 验证
                    with open('agent/tools.py', 'r', encoding='utf-8') as f:
                        test_content = f.read(200)
                        if '宪法' in test_content:
                            print("✅ 验证: 中文字符恢复正常")
                        else:
                            print("⚠️  验证: 中文字符可能仍有问题")
                    
                    return True
                    
            except UnicodeDecodeError:
                continue
        
        print("❌ 无法自动修复编码")
        return False
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

if __name__ == "__main__":
    fix_encoding()