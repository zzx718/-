#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
毕业论文Markdown转Word工具
根据湖南农业大学毕业论文格式要求生成Word文档
"""

import re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn


class ThesisDocxGenerator:
    """论文Word文档生成器"""
    
    def __init__(self):
        self.doc = Document()
        self.setup_page_layout()
        
    def setup_page_layout(self):
        """设置页面布局"""
        for section in self.doc.sections:
            section.top_margin = Cm(2.54)
            section.bottom_margin = Cm(2.54)
            section.left_margin = Cm(2.6)
            section.right_margin = Cm(2.6)
    
    def add_title(self, text, level=1):
        """添加标题"""
        p = self.doc.add_paragraph()
        
        if level == 1:
            # 一级标题：小三号黑体（15磅）
            run = p.add_run(text)
            run.font.name = 'Times New Roman'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
            run.font.size = Pt(15)
            run.bold = True
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(6)
        elif level == 2:
            # 二级标题：四号黑体（14磅）
            run = p.add_run(text)
            run.font.name = 'Times New Roman'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
            run.font.size = Pt(14)
            run.bold = True
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
        elif level == 3:
            # 三级标题：小四号黑体（12磅）
            run = p.add_run(text)
            run.font.name = 'Times New Roman'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
            run.font.size = Pt(12)
            run.bold = True
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
        
        # 固定行距22磅
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        p.paragraph_format.line_spacing = Pt(22)
        
    def add_paragraph(self, text, indent=True, bold_prefix=None, alignment=None):
        """添加段落"""
        if not text.strip():
            return
            
        p = self.doc.add_paragraph()
        
        # 固定行距22磅
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        p.paragraph_format.line_spacing = Pt(22)
        
        # 首行缩进
        if indent:
            p.paragraph_format.first_line_indent = Pt(24)  # 2字符
        
        if alignment:
            p.alignment = alignment
        
        # 处理粗体前缀（如"摘要："）
        if bold_prefix:
            # 粗体部分
            run1 = p.add_run(bold_prefix)
            run1.font.name = 'Times New Roman'
            run1._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
            run1.font.size = Pt(12)
            run1.bold = True
            # 正文部分
            run2 = p.add_run(text)
            run2.font.name = 'Times New Roman'
            run2._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
            run2.font.size = Pt(12)
        else:
            # 普通段落
            run = p.add_run(text)
            run.font.name = 'Times New Roman'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
            run.font.size = Pt(12)
    
    def add_reference(self, text):
        """添加参考文献条目"""
        p = self.doc.add_paragraph()
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        p.paragraph_format.line_spacing = Pt(22)
        
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        run.font.size = Pt(10.5)  # 五号字
        
    def parse_and_generate(self, md_file, output_file):
        """解析Markdown文件并生成Word文档"""
        with open(md_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            
            # 跳过空行
            if not line:
                i += 1
                continue
            
            # 处理三级标题 (x.x.x 格式)
            if re.match(r'^\d+\.\d+\.\d+\s+', line):
                self.add_title(line, level=3)
                i += 1
                continue
            
            # 处理二级标题 (x.x 格式)
            if re.match(r'^\d+\.\d+\s+', line):
                self.add_title(line, level=2)
                i += 1
                continue
            
            # 处理一级标题 (x 格式)
            if re.match(r'^\d+\s+[^\d]', line):
                self.add_title(line, level=1)
                i += 1
                continue
            
            # 处理摘要
            if line.startswith('摘　要：') or line.startswith('摘要：'):
                content = line.replace('摘　要：', '').replace('摘要：', '')
                self.add_paragraph(content, indent=True, bold_prefix='摘　要：')
                i += 1
                continue
            
            # 处理关键词
            if line.startswith('关键词：'):
                content = line.replace('关键词：', '')
                self.add_paragraph(content, indent=True, bold_prefix='关键词：')
                i += 1
                continue
            
            # 处理Abstract
            if line.startswith('Abstract:') or line.startswith('Abstract：'):
                content = line.replace('Abstract:', '').replace('Abstract：', '').strip()
                self.add_paragraph(content, indent=True, bold_prefix='Abstract: ')
                i += 1
                continue
            
            # 处理Key words
            if line.startswith('Key words:'):
                content = line.replace('Key words:', '').strip()
                self.add_paragraph(content, indent=True, bold_prefix='Key words: ')
                i += 1
                continue
            
            # 处理参考文献标题
            if line == '参考文献':
                self.add_title('参考文献', level=1)
                i += 1
                continue
            
            # 处理参考文献条目
            if re.match(r'^\[\d+\]', line):
                self.add_reference(line)
                i += 1
                continue
            
            # 处理致谢标题
            if line == '致　　谢':
                self.add_title('致　　谢', level=1)
                i += 1
                continue
            
            # 跳过图表占位符
            if '【此处插入图' in line or '【此处插入表' in line:
                i += 1
                continue
            
            # 跳过图表说明行（Fig.x 或 Table.x）
            if re.match(r'^Fig\.\d+|^Table\s*\d+', line):
                i += 1
                continue
            
            # 跳过以"图x"或"表x"开头的行
            if re.match(r'^图\d+|^表\d+', line):
                i += 1
                continue
            
            # 普通段落
            # 跳过过短的行（可能是标题或格式行）
            if len(line.strip()) > 5:
                self.add_paragraph(line)
            
            i += 1
        
        # 保存文档
        self.doc.save(output_file)
        print(f"✅ Word文档已生成: {output_file}")


def main():
    """主函数"""
    import os
    
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    md_file = os.path.join(current_dir, '毕业论文_初稿.md')
    output_file = os.path.join(current_dir, '毕业论文_格式化版.docx')
    
    generator = ThesisDocxGenerator()
    generator.parse_and_generate(md_file, output_file)


if __name__ == '__main__':
    main()
