import yaml
from openai import OpenAI

print("🧪 测试API配置")
print("=" * 40)

try:
    # 加载配置
    with open('config/secrets.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    api_key = config['deepseek']['api_key']
    
    if api_key == 'your-deepseek-api-key-here':
        print("❌ 请配置API密钥")
        print("编辑 config/secrets.yaml 文件")
    else:
        print(f"✅ API密钥已配置")
        print(f"密钥: {api_key[:8]}...{api_key[-4:]}")
        
        # 测试连接
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "回复'连接成功'"}],
            max_tokens=10
        )
        
        print(f"✅ API连接成功！")
        print(f"回复: {response.choices[0].message.content}")
        
except Exception as e:
    print(f"❌ 测试失败: {e}")
