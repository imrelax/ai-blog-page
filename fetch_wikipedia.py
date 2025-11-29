#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re
import os
import time
from datetime import datetime
from pathlib import Path
import html
from urllib.parse import quote

class WikipediaFetcher:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def clean_wiki_text(self, text):
        """深度清理维基文本格式"""
        if not text:
            return ""
        
        # 移除HTML注释
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        
        # 移除维基链接格式 [[链接|显示文本]] -> 显示文本
        text = re.sub(r'\[\[([^\|\]]+)\|([^\]]+)\]\]', r'\2', text)
        text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)
        
        # 移除外部链接 [http://example.com 显示文本] -> 显示文本
        text = re.sub(r'\[https?://[^\s\]]+\s+([^\]]+)\]', r'\1', text)
        text = re.sub(r'\[https?://[^\s\]]+\]', '', text)
        
        # 移除模板 {{模板名|参数}}
        text = re.sub(r'\{\{[^}]+\}\}', '', text)
        
        # 移除引用标签 <ref>...</ref>
        text = re.sub(r'<ref[^>]*>.*?</ref>', '', text, flags=re.DOTALL)
        text = re.sub(r'<ref[^>]*/>', '', text)
        
        # 移除表格 {| ... |}
        text = re.sub(r'\{\|.*?\|\}', '', text, flags=re.DOTALL)
        
        # 移除HTML实体
        text = html.unescape(text)
        
        # 移除多余的空格和换行
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'\s{2,}', ' ', text)
        
        # 移除章节标题的==标记
        text = re.sub(r'=+\s*(.*?)\s*=+', r'## \1', text)
        
        return text.strip()
    
    def get_popular_articles(self, limit=50):
        """获取科技AI相关的热门文章列表"""
        print("获取科技AI相关的热门文章列表...")
        
        # 简体中文Wikipedia的科技AI相关文章
        tech_ai_topics = [
            # 人工智能核心领域
            "人工智能", "机器学习", "深度学习", "神经网络", "自然语言处理",
            "计算机视觉", "强化学习", "监督学习", "无监督学习", "半监督学习",
            "迁移学习", "联邦学习", "元学习", "知识表示", "推理系统",
            
            # AI应用领域
            "自动驾驶", "人脸识别", "语音识别", "机器翻译", "推荐系统",
            "聊天机器人", "生成对抗网络", "大语言模型", "Transformer模型",
            "BERT模型", "GPT模型", "扩散模型", "Stable Diffusion",
            
            # 计算机科学基础
            "计算机科学", "算法", "数据结构", "编程语言", "Python",
            "TensorFlow", "PyTorch", "Scikit-learn", "Keras", "计算机编程",
            "软件工程", "数据库", "操作系统", "计算机网络", "云计算",
            "分布式计算", "并行计算", "量子计算", "边缘计算", "物联网",
            
            # 数学和理论基础
            "数学", "线性代数", "概率论", "统计学", "微积分",
            "离散数学", "图论", "优化理论", "信息论", "博弈论",
            "计算复杂性理论", "数值分析", "最优化方法",
            
            # 相关科技领域
            "数据科学", "大数据", "数据分析", "数据挖掘", "数据可视化",
            "计算机图形学", "数字图像处理", "信号处理", "模式识别",
            "机器人学", "自动化", "智能制造", "智慧城市", "数字孪生",
            "区块链", "加密货币", "元宇宙", "增强现实", "虚拟现实",
            "计算机安全", "网络安全", "密码学", "隐私保护"
        ]
        
        return tech_ai_topics[:limit]
    
    def fetch_article(self, title):
        """从Wikipedia API获取完整文章内容"""
        print(f"获取文章: {title}")
        
        # Wikipedia API endpoint
        url = "https://zh.wikipedia.org/w/api.php"
        
        params = {
            'action': 'query',
            'format': 'json',
            'titles': title,
            'prop': 'extracts',
            'exintro': False,  # 获取完整内容，不仅仅是简介
            'explaintext': True,
            'exsectionformat': 'plain',
            'exlimit': 'max',  # 获取最大限制的内容
            'exchars': 1200    # 增加字符限制以获取更多内容
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # 提取页面内容
            pages = data.get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                if page_id != '-1':  # 跳过不存在的页面
                    content = page_data.get('extract', '')
                    if content:
                        return content
            
            return None
            
        except Exception as e:
            print(f"获取文章 {title} 失败: {e}")
            return None
    
    def convert_to_hugo_format(self, title, content, category="wikipedia"):
        """转换为Hugo文章格式"""
        # 清理标题用于文件名
        clean_title = re.sub(r'[^\w\u4e00-\u9fff-]', '_', title)
        clean_title = clean_title[:50]
        
        # 清理内容
        cleaned_content = self.clean_wiki_text(content)
        
        # 提取描述
        description = cleaned_content[:150] + '...' if len(cleaned_content) > 150 else cleaned_content
        description = description.replace('"', "'")
        
        # 根据主题分类标签
        tags = ["维基百科", "知识库"]
        if "人工" in title or "智能" in title:
            tags.extend(["人工智能", "AI"])
        elif "学习" in title:
            tags.extend(["机器学习", "深度学习"])
        elif "数学" in title:
            tags.append("数学")
        elif "物理" in title:
            tags.append("物理学")
        elif "化学" in title:
            tags.append("化学")
        
        # Hugo front matter
        front_matter = f"""---
title: "{title}"
date: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')}
description: "{description}"
draft: false
author: "Wikipedia"
cover: ""
tags: {tags}
categories: ["{category}"]
theme: "light"
---

"""
        
        return front_matter + cleaned_content, clean_title
    
    def save_article(self, title, content, category="wikipedia"):
        """保存文章到文件"""
        hugo_content, clean_title = self.convert_to_hugo_format(title, content, category)
        
        # 创建分类目录
        category_dir = self.output_dir / category
        category_dir.mkdir(exist_ok=True)
        
        filename = category_dir / f"{clean_title}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(hugo_content)
        
        print(f"已保存: {filename}")
        return filename
    
    def fetch_multiple_articles(self, topics, delay=1):
        """批量获取多篇文章"""
        successful_count = 0
        
        for topic in topics:
            content = self.fetch_article(topic)
            if content:
                self.save_article(topic, content)
                successful_count += 1
                time.sleep(delay)  # 礼貌延迟
            else:
                print(f"跳过 {topic} (未找到内容)")
        
        return successful_count

def main():
    # 设置输出目录
    output_dir = "/Volumes/文件/github/ai-blog-page/content"
    
    # 创建获取器实例
    fetcher = WikipediaFetcher(output_dir)
    
    # 获取科技AI相关的热门主题
    print("=== Wikipedia科技AI文章批量获取工具 ===")
    print("专注于简体中文、科技AI相关内容，获取详细文章内容")
    
    # 获取50个科技AI相关主题
    topics = fetcher.get_popular_articles(50)
    
    print(f"\n开始获取 {len(topics)} 篇科技AI相关文章...")
    print("=" * 60)
    
    # 批量获取文章
    successful = fetcher.fetch_multiple_articles(topics)
    
    print("=" * 60)
    print(f"完成! 成功获取 {successful} 篇科技AI相关文章")
    print(f"文章已保存到: {output_dir}/wikipedia/")
    
    # 显示一些使用提示
    print("\n使用说明:")
    print("1. 运行 'hugo server -D' 查看包含新文章的网站")
    print("2. 所有文章默认设置为 draft: false (立即发布)")
    print("3. 文章保存在 content/wikipedia/ 目录下")
    print("4. 内容为简体中文，专注于科技AI相关领域")
    print("5. 获取的是详细文章内容，不仅仅是标题信息")

if __name__ == "__main__":
    main()