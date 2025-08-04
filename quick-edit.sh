#!/bin/bash
# 快速编辑脚本 - 服务器端内容管理工具 (VS Code + 标签树状支持)

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_DIR="/var/www/cuhkstudy"
cd "$PROJECT_DIR"

# 编辑器配置
EDITOR_CHOICE=""

echo -e "${BLUE}=== CUHKstudy 增强编辑工具 ===${NC}"
echo -e "${CYAN}📝 支持VS Code远程编辑 + 🏷️ 标签树状管理${NC}"
echo

# 选择编辑器
choose_editor() {
    echo -e "${PURPLE}🔧 选择编辑器：${NC}"
    echo "1. VS Code (推荐，支持语法高亮和实时预览)"
    echo "2. Nano (轻量级，服务器本地编辑)"
    echo "3. Vim (高级用户)"
    echo
    
    read -p "选择编辑器 (1-3): " editor_choice
    
    case $editor_choice in
        1) 
            EDITOR_CHOICE="vscode"
            setup_vscode
            ;;
        2) EDITOR_CHOICE="nano" ;;
        3) EDITOR_CHOICE="vim" ;;
        *) 
            echo -e "${YELLOW}使用默认编辑器 nano${NC}"
            EDITOR_CHOICE="nano"
            ;;
    esac
    echo
}

# 设置VS Code远程编辑
setup_vscode() {
    echo -e "${BLUE}🔧 设置VS Code远程编辑...${NC}"
    
    # 检查code命令是否可用
    if ! command -v code &> /dev/null; then
        echo -e "${YELLOW}正在安装VS Code Server...${NC}"
        
        # 下载并安装VS Code Server
        curl -fsSL https://code-server.dev/install.sh | sh
        
        # 启动code-server
        echo -e "${BLUE}启动VS Code Server...${NC}"
        nohup code-server --bind-addr 0.0.0.0:8080 --auth none --disable-telemetry > /tmp/code-server.log 2>&1 &
        
        echo -e "${GREEN}✅ VS Code Server已启动${NC}"
        echo -e "${CYAN}📍 访问地址: http://localhost:8888 (通过SSH转发)${NC}"
        echo -e "${YELLOW}💡 在本地运行: ssh -L 8888:localhost:8080 root@你的服务器IP${NC}"
        echo
    fi
    
    # 安装有用的VS Code扩展
    code-server --install-extension ms-vscode.markdown-preview-enhanced || true
    code-server --install-extension yzhang.markdown-all-in-one || true
    code-server --install-extension davidanson.vscode-markdownlint || true
}

# 解析Front Matter中的标签
extract_tags() {
    local file="$1"
    if [[ -f "$file" ]]; then
        # 提取tags行并解析
        grep -E "^tags:" "$file" 2>/dev/null | sed 's/tags:\s*\[\(.*\)\]/\1/' | tr ',' '\n' | sed 's/[" ]//g' | grep -v '^$'
    fi
}

# 解析Front Matter中的title
extract_title() {
    local file="$1"
    if [[ -f "$file" ]]; then
        grep -E "^title:" "$file" 2>/dev/null | sed 's/title:\s*["'"'"']\(.*\)["'"'"']/\1/' | head -1
    fi
}

# 按标签展示文章树状结构
show_tag_tree() {
    echo -e "${BLUE}🏷️ 按标签分类的文章树状结构：${NC}"
    echo
    
    # 创建临时文件存储标签映射
    local tag_file="/tmp/tag_mapping.txt"
    local no_tag_articles=()
    
    > "$tag_file"
    
    # 遍历所有markdown文件
    while IFS= read -r -d '' file; do
        local title=$(extract_title "$file")
        local tags=$(extract_tags "$file")
        
        if [[ -z "$title" ]]; then
            title=$(basename "$file" .md)
        fi
        
        if [[ -n "$tags" ]]; then
            while IFS= read -r tag; do
                [[ -n "$tag" ]] && echo "$tag|$file|$title" >> "$tag_file"
            done <<< "$tags"
        else
            no_tag_articles+=("$file|$title")
        fi
    done < <(find content -name "*.md" -type f -print0)
    
    # 按标签分组显示
    if [[ -s "$tag_file" ]]; then
        local current_tag=""
        local count=1
        
        sort "$tag_file" | while IFS='|' read -r tag file title; do
            if [[ "$tag" != "$current_tag" ]]; then
                current_tag="$tag"
                echo -e "${PURPLE}📂 $tag${NC}"
            fi
            
            echo -e "   ${count}. ${CYAN}$title${NC} ${YELLOW}($file)${NC}"
            ((count++))
        done
    fi
    
    # 显示无标签文章
    if [[ ${#no_tag_articles[@]} -gt 0 ]]; then
        echo -e "${PURPLE}📂 未分类${NC}"
        local count=1
        for article in "${no_tag_articles[@]}"; do
            IFS='|' read -r file title <<< "$article"
            echo -e "   ${count}. ${CYAN}$title${NC} ${YELLOW}($file)${NC}"
            ((count++))
        done
    fi
    
    rm -f "$tag_file"
    echo
}

# 按标签搜索文章
search_by_tag() {
    echo -e "${BLUE}🔍 按标签搜索文章：${NC}"
    echo
    
    # 显示所有可用标签
    echo -e "${PURPLE}📋 可用标签：${NC}"
    local all_tags=()
    
    while IFS= read -r -d '' file; do
        local tags=$(extract_tags "$file")
        if [[ -n "$tags" ]]; then
            while IFS= read -r tag; do
                [[ -n "$tag" ]] && all_tags+=("$tag")
            done <<< "$tags"
        fi
    done < <(find content -name "*.md" -type f -print0)
    
    # 去重并排序显示标签
    printf '%s\n' "${all_tags[@]}" | sort -u | nl -w2 -s". "
    echo
    
    read -p "输入标签名称或编号: " tag_input
    
    # 如果输入的是数字，转换为标签名
    if [[ "$tag_input" =~ ^[0-9]+$ ]]; then
        local tag_name=$(printf '%s\n' "${all_tags[@]}" | sort -u | sed -n "${tag_input}p")
    else
        local tag_name="$tag_input"
    fi
    
    if [[ -z "$tag_name" ]]; then
        echo -e "${RED}❌ 无效的标签${NC}"
        return 1
    fi
    
    echo -e "${BLUE}📄 标签 '${tag_name}' 下的文章：${NC}"
    echo
    
    local found_articles=()
    while IFS= read -r -d '' file; do
        local tags=$(extract_tags "$file")
        if [[ -n "$tags" ]] && echo "$tags" | grep -q "^$tag_name$"; then
            local title=$(extract_title "$file")
            [[ -z "$title" ]] && title=$(basename "$file" .md)
            found_articles+=("$file|$title")
        fi
    done < <(find content -name "*.md" -type f -print0)
    
    if [[ ${#found_articles[@]} -eq 0 ]]; then
        echo -e "${YELLOW}该标签下没有找到文章${NC}"
        return 1
    fi
    
    local count=1
    for article in "${found_articles[@]}"; do
        IFS='|' read -r file title <<< "$article"
        echo -e "${count}. ${CYAN}$title${NC} ${YELLOW}($file)${NC}"
        ((count++))
    done
    echo
    
    read -p "选择文章编号进行编辑 (回车返回): " article_num
    if [[ -n "$article_num" && "$article_num" -le ${#found_articles[@]} ]]; then
        local selected_article="${found_articles[$((article_num-1))]}"
        IFS='|' read -r file title <<< "$selected_article"
        edit_file "$file"
    fi
}

# 检查Git状态
check_git_status() {
    if [[ -n $(git status --porcelain) ]]; then
        echo -e "${YELLOW}⚠️  检测到未提交的更改：${NC}"
        git status --short
        echo
        read -p "是否先提交这些更改？(y/n): " commit_first
        if [[ $commit_first == "y" ]]; then
            read -p "提交信息: " commit_msg
            git add .
            git commit -m "$commit_msg"
            git push
            echo -e "${GREEN}✅ 更改已提交并推送${NC}"
        fi
    fi
}

# 列出所有markdown文件
list_content() {
    echo -e "${BLUE}📄 可编辑的内容文件：${NC}"
    echo
    find content -name "*.md" -type f | grep -E "\.(md)$" | sort | nl -w2 -s". "
    echo
}

# 快速搜索文件
search_content() {
    echo -e "${BLUE}🔍 搜索内容文件：${NC}"
    read -p "输入搜索关键词: " keyword
    echo
    find content -name "*.md" -type f | xargs grep -l "$keyword" | nl -w2 -s". "
    echo
}

# 编辑文件
edit_file() {
    local file_path="$1"
    
    if [[ ! -f "$file_path" ]]; then
        echo -e "${RED}❌ 文件不存在: $file_path${NC}"
        return 1
    fi
    
    echo -e "${BLUE}📝 编辑文件: $file_path${NC}"
    
    # 备份当前文件
    cp "$file_path" "$file_path.backup.$(date +%Y%m%d_%H%M%S)"
    
    case "$EDITOR_CHOICE" in
        "vscode")
            echo -e "${CYAN}🚀 在VS Code中打开文件...${NC}"
            echo -e "${YELLOW}💡 文件将在浏览器中的VS Code编辑器打开${NC}"
            echo -e "${YELLOW}📍 访问: http://localhost:8888${NC}"
            echo
            
            # 使用code-server打开文件
            if command -v code-server &> /dev/null; then
                code-server "$file_path" &
                echo -e "${GREEN}✅ VS Code已打开，请在浏览器中编辑${NC}"
                echo -e "${BLUE}⏳ 编辑完成后按任意键继续...${NC}"
                read -n 1 -s
            else
                echo -e "${RED}❌ VS Code Server未正确安装，回退到nano编辑器${NC}"
                nano "$file_path"
            fi
            ;;
        "vim")
            echo -e "${YELLOW}📝 使用Vim编辑器 (按 :wq 保存退出)${NC}"
            vim "$file_path"
            ;;
        *)
            echo -e "${YELLOW}📝 使用Nano编辑器 (Ctrl+X, Y, Enter 保存退出)${NC}"
            nano "$file_path"
            ;;
    esac
    
    # 检查文件是否被修改
    if ! cmp -s "$file_path" "$file_path.backup."*; then
        echo -e "${GREEN}✅ 文件已修改${NC}"
        
        # 询问是否预览
        read -p "是否立即重新生成网站？(y/n): " rebuild
        if [[ $rebuild == "y" ]]; then
            echo -e "${BLUE}🔨 重新生成网站...${NC}"
            hugo --minify
            echo -e "${GREEN}✅ 网站已重新生成${NC}"
        fi
        
        # 询问是否提交
        read -p "是否提交更改到Git？(y/n): " commit_changes
        if [[ $commit_changes == "y" ]]; then
            read -p "提交信息 (默认: 更新内容): " commit_msg
            commit_msg=${commit_msg:-"更新内容"}
            
            git add "$file_path"
            git commit -m "$commit_msg"
            
            read -p "是否推送到GitHub？(y/n): " push_changes
            if [[ $push_changes == "y" ]]; then
                git push
                echo -e "${GREEN}✅ 更改已推送到GitHub${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}ℹ️  文件未修改${NC}"
    fi
    
    # 清理备份文件
    rm -f "$file_path.backup."*
}

# 创建新文章
create_new_post() {
    echo -e "${BLUE}📝 创建新文章${NC}"
    echo
    
    # 选择目录
    echo "选择文章目录："
    echo "1. main (主要内容)"
    echo "2. ugfn (大学国文)"
    echo "3. ugfh (大学中史)"
    echo "4. mess (杂聊)"
    echo "5. ai-literacy (AI素养)"
    
    read -p "选择目录 (1-5): " dir_choice
    
    case $dir_choice in
        1) content_dir="main" ;;
        2) content_dir="ugfn" ;;
        3) content_dir="ugfh" ;;
        4) content_dir="mess" ;;
        5) content_dir="ai-literacy" ;;
        *) echo -e "${RED}❌ 无效选择${NC}"; return 1 ;;
    esac
    
    read -p "文章标题: " title
    read -p "文件名 (不含.md): " filename
    
    # 创建文件路径
    file_path="content/$content_dir/$filename.md"
    
    if [[ -f "$file_path" ]]; then
        echo -e "${RED}❌ 文件已存在: $file_path${NC}"
        return 1
    fi
    
    # 创建Front Matter
    cat > "$file_path" << EOF
---
title: "$title"
date: $(date +%Y-%m-%dT%H:%M:%S%z)
draft: false
description: ""
tags: []
---

# $title

在这里开始编写你的内容...

EOF
    
    echo -e "${GREEN}✅ 新文章已创建: $file_path${NC}"
    edit_file "$file_path"
}

# 主菜单
main_menu() {
    while true; do
        echo -e "${BLUE}=== 主菜单 ===${NC}"
        echo -e "${PURPLE}🏷️ 标签管理：${NC}"
        echo "1. 按标签树状显示所有文章"
        echo "2. 按标签搜索文章"
        echo
        echo -e "${CYAN}📄 文件管理：${NC}"
        echo "3. 列出所有内容文件"
        echo "4. 关键词搜索文章内容"
        echo "5. 直接输入文件路径编辑"
        echo "6. 创建新文章"
        echo
        echo -e "${GREEN}🔧 系统操作：${NC}"
        echo "7. 切换编辑器"
        echo "8. 检查Git状态"
        echo "9. 同步GitHub最新内容"
        echo "10. 重新生成网站"
        echo "0. 退出"
        echo
        
        read -p "请选择操作 (0-10): " choice
        echo
        
        case $choice in
            1)
                show_tag_tree
                ;;
            2)
                search_by_tag
                ;;
            3)
                list_content
                read -p "输入文件编号进行编辑 (回车返回菜单): " file_num
                if [[ -n $file_num ]]; then
                    file_path=$(find content -name "*.md" -type f | sort | sed -n "${file_num}p")
                    if [[ -n $file_path ]]; then
                        edit_file "$file_path"
                    else
                        echo -e "${RED}❌ 无效的文件编号${NC}"
                    fi
                fi
                ;;
            4)
                search_content
                read -p "输入文件编号进行编辑 (回车返回菜单): " file_num
                if [[ -n $file_num ]]; then
                    file_path=$(find content -name "*.md" -type f | xargs grep -l "$keyword" | sed -n "${file_num}p")
                    if [[ -n $file_path ]]; then
                        edit_file "$file_path"
                    else
                        echo -e "${RED}❌ 无效的文件编号${NC}"
                    fi
                fi
                ;;
            5)
                read -p "输入文件路径: " file_path
                edit_file "$file_path"
                ;;
            6)
                create_new_post
                ;;
            7)
                choose_editor
                ;;
            8)
                check_git_status
                ;;
            9)
                echo -e "${BLUE}🔄 从GitHub同步最新内容...${NC}"
                git pull
                hugo --minify
                echo -e "${GREEN}✅ 同步完成${NC}"
                ;;
            10)
                echo -e "${BLUE}🔨 重新生成网站...${NC}"
                hugo --minify
                echo -e "${GREEN}✅ 网站已重新生成${NC}"
                ;;
            0)
                echo -e "${GREEN}👋 再见！${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ 无效选择，请重试${NC}"
                ;;
        esac
        echo
    done
}

# 检查依赖
if ! command -v nano &> /dev/null; then
    echo -e "${YELLOW}⚠️  安装nano编辑器...${NC}"
    apt update && apt install -y nano
fi

# 首次运行选择编辑器
choose_editor

# 首次运行检查Git状态
check_git_status

# 启动主菜单
main_menu