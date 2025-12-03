#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import shutil
from pathlib import Path

# 分类映射
def get_category_and_tags(filename):
    """根据文件名确定分类和标签"""
    name = filename.lower()
    
    # AI/ML 相关
    if any(keyword in name for keyword in ['ai', '人工智能', '机器学习', '深度学习', '神经网络', 
                                        '自然语言处理', '计算机视觉', '强化学习', '监督学习',
                                        '无监督学习', '迁移学习', '联邦学习', '生成对抗',
                                        'transformer', 'bert', 'gpt', '扩散模型', 'stable diffusion']):
        return 'ai-ml', ['人工智能', '机器学习', 'AI']
    
    # 编程开发
    elif any(keyword in name for keyword in ['python', 'tensorflow', 'pytorch', 'keras', 'scikit',
                                           '编程', '软件工程', '算法', '数据结构', '操作系统',
                                           '计算机网络', '数据库', '分布式计算', '并行计算']):
        return 'programming', ['编程', '开发', '技术']
    
    # 数学基础
    elif any(keyword in name for keyword in ['数学', '线性代数', '概率论', '统计学', '微积分',
                                            '离散数学', '图论', '优化理论', '信息论', '博弈论']):
        return 'mathematics', ['数学', '理论', '基础']
    
    # 数据科学
    elif any(keyword in name for keyword in ['数据科学', '大数据', '数据分析', '数据挖掘', '数据可视化',
                                           '物联网', '云计算', '边缘计算']):
        return 'data-science', ['数据', '分析', '科学']
    
    # 教程指南
    elif any(keyword in name for keyword in ['教程', '指南', '入门', '实战', '学习']):
        return 'tutorials', ['教程', '指南', '学习']
    
    # 默认分类为百科知识
    else:
        return 'encyclopedia', ['百科', '知识', '概念']

def get_cover_image(filename):
    """根据文章主题获取相应的缩略图"""
    name = filename.lower()
    
    # AI/ML 相关缩略图
    if any(keyword in name for keyword in ['ai', '人工智能', '机器学习', '深度学习']):
        return "https://images.unsplash.com/photo-1573164713714-d95e436ab8d6?w=800&h=400&fit=crop"
    
    # 编程开发
    elif any(keyword in name for keyword in ['python', '编程', '软件工程']):
        return "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=800&h=400&fit=crop"
    
    # 数学基础
    elif any(keyword in name for keyword in ['数学', '线性代数', '概率论']):
        return "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=800&h=400&fit=crop"
    
    # 数据科学
    elif any(keyword in name for keyword in ['数据', '分析', '科学']):
        return "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=400&fit=crop"
    
    # 默认缩略图
    return "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&h=400&fit=crop"

def update_article_metadata(filepath, category, tags, cover_image):
    """更新文章的元数据"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新front matter
    front_matter = f"""---
title: "{Path(filepath).stem}"
date: 2025-11-29T00:00:00+08:00
description: "{Path(filepath).stem} - 详细的技术文章和知识介绍"
draft: false
author: "AI知识库"
cover: "{cover_image}"
tags: {tags}
categories: ["{category}"]
theme: "light"
---
"""
    
    # 移除旧的front matter（如果有）
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2].strip()
    
    # 写入新的内容
    new_content = front_matter + '\n' + content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

def organize_content():
    """整理所有内容"""
    content_dir = Path("/Volumes/文件/github/ai-blog-page/content")
    
    # 处理所有markdown文件
    for md_file in content_dir.rglob("*.md"):
        if md_file.name == "_index.md" or md_file.parent.name == "categories":
            continue
        
        print(f"处理: {md_file.name}")
        
        # 获取分类和标签
        category, tags = get_category_and_tags(md_file.name)
        cover_image = get_cover_image(md_file.name)
        
        # 更新元数据
        update_article_metadata(str(md_file), category, tags, cover_image)
        
        # 移动到分类目录
        target_dir = content_dir / "categories" / category
        target_dir.mkdir(exist_ok=True)
        
        # 移动文件
        shutil.move(str(md_file), str(target_dir / md_file.name))
        
        print(f"  -> 移动到: {category}")
        print(f"  -> 标签: {tags}")
        print(f"  -> 缩略图: {cover_image}")

if __name__ == "__main__":
    print("开始整理博客内容...")
    print("=" * 50)
    organize_content()
    print("=" * 50)
    print("内容整理完成！")
    print("所有文章已分类并添加了缩略图和标签")