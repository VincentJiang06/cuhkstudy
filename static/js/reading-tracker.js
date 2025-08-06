/**
 * CUHKstudy 阅读量统计客户端
 * 轻量级、隐私友好的前端统计脚本
 */

(function() {
    'use strict';
    
    // 配置
    const CONFIG = {
        apiBaseUrl: window.location.protocol + '//' + window.location.host,
        trackEndpoint: '/api/track',
        statsEndpoint: '/api/stats',
        debounceTime: 1000, // 防抖时间
        storageKey: 'cuhkstudy_reading_stats'
    };
    
    // 统计管理器
    class ReadingTracker {
        constructor() {
            this.tracked = new Set();
            this.viewCounts = new Map();
            this.init();
        }
        
        init() {
            // 加载已有统计数据
            this.loadStoredStats();
            
            // 跟踪当前页面
            this.trackPageView();
            
            // 添加卡片点击跟踪
            this.setupCardTracking();
            
            // 显示阅读量
            this.displayReadingCounts();
            
            // 定期更新显示
            setInterval(() => this.displayReadingCounts(), 30000);
        }
        
        loadStoredStats() {
            try {
                const stored = localStorage.getItem(CONFIG.storageKey);
                if (stored) {
                    const data = JSON.parse(stored);
                    this.viewCounts = new Map(data.viewCounts || []);
                }
            } catch (e) {
                console.warn('读取统计数据失败:', e);
            }
        }
        
        saveStats() {
            try {
                const data = {
                    viewCounts: Array.from(this.viewCounts.entries()),
                    lastUpdate: Date.now()
                };
                localStorage.setItem(CONFIG.storageKey, JSON.stringify(data));
            } catch (e) {
                console.warn('保存统计数据失败:', e);
            }
        }
        
        async trackPageView() {
            const url = window.location.pathname;
            const title = document.title;
            
            // 避免重复跟踪
            if (this.tracked.has(url)) return;
            this.tracked.add(url);
            
            try {
                const response = await fetch(CONFIG.apiBaseUrl + CONFIG.trackEndpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        url: url,
                        title: title,
                        timestamp: Date.now()
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    console.log('📖 页面访问已记录:', data.message);
                    // 更新本地计数
                    const current = this.viewCounts.get(url) || 0;
                    this.viewCounts.set(url, current + 1);
                    this.saveStats();
                }
            } catch (error) {
                console.warn('记录页面访问失败:', error);
                // 即使API失败，也在本地记录
                const current = this.viewCounts.get(url) || 0;
                this.viewCounts.set(url, current + 1);
                this.saveStats();
            }
        }
        
        setupCardTracking() {
            // 监听所有链接点击
            document.addEventListener('click', (event) => {
                const link = event.target.closest('a');
                if (!link) return;
                
                const href = link.getAttribute('href');
                if (!href || href.startsWith('#') || href.startsWith('http')) return;
                
                // 记录卡片点击
                this.trackCardClick(href, link.textContent.trim());
            });
        }
        
        async trackCardClick(url, title) {
            // 防抖处理
            if (this.tracked.has(`click_${url}`)) return;
            this.tracked.add(`click_${url}`);
            
            setTimeout(() => {
                this.tracked.delete(`click_${url}`);
            }, CONFIG.debounceTime);
            
            try {
                await fetch(CONFIG.apiBaseUrl + CONFIG.trackEndpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        url: url,
                        title: title,
                        type: 'card_click',
                        timestamp: Date.now()
                    })
                });
                
                // 更新本地显示
                const current = this.viewCounts.get(url) || 0;
                this.viewCounts.set(url, current + 1);
                this.updateCardCount(url, current + 1);
                this.saveStats();
                
            } catch (error) {
                console.warn('记录卡片点击失败:', error);
            }
        }
        
        async fetchStats(url = null) {
            try {
                const endpoint = url 
                    ? `${CONFIG.statsEndpoint}?url=${encodeURIComponent(url)}`
                    : CONFIG.statsEndpoint;
                    
                const response = await fetch(CONFIG.apiBaseUrl + endpoint);
                if (response.ok) {
                    return await response.json();
                }
            } catch (error) {
                console.warn('获取统计数据失败:', error);
            }
            return null;
        }
        
        async displayReadingCounts() {
            // 查找所有需要显示阅读量的元素
            const links = document.querySelectorAll('a[href^="/"]');
            
            for (const link of links) {
                const url = link.getAttribute('href');
                if (!url || url === '/' || url.includes('#')) continue;
                
                // 跳过已经添加了阅读量的链接
                if (link.querySelector('.reading-count')) continue;
                
                // 获取统计数据
                let viewCount = this.viewCounts.get(url) || 0;
                
                // 尝试从服务器获取最新数据（减少频率，避免过多请求）
                try {
                    const stats = await this.fetchStats(url);
                    if (stats && stats.total_views) {
                        viewCount = stats.total_views;
                        this.viewCounts.set(url, viewCount);
                    }
                } catch (error) {
                    // 忽略网络错误，使用本地数据
                }
                
                // 只为有阅读量的链接添加显示
                if (viewCount > 0) {
                    this.addReadingCountBadge(link, viewCount);
                }
            }
            
            this.saveStats();
        }
        
        addReadingCountBadge(element, count) {
            // 避免重复添加
            if (element.querySelector('.reading-count')) return;
            
            const badge = document.createElement('span');
            badge.className = 'reading-count';
            badge.innerHTML = `<span class="reading-icon">👁</span> ${this.formatCount(count)}`;
            
            // 样式
            badge.style.cssText = `
                display: inline-flex;
                align-items: center;
                gap: 4px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                font-size: 12px;
                padding: 2px 8px;
                border-radius: 12px;
                margin-left: 8px;
                font-weight: 500;
                box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
                transition: all 0.2s ease;
            `;
            
            // 添加悬停效果
            badge.addEventListener('mouseenter', () => {
                badge.style.transform = 'scale(1.1)';
                badge.style.boxShadow = '0 4px 8px rgba(102, 126, 234, 0.4)';
            });
            
            badge.addEventListener('mouseleave', () => {
                badge.style.transform = 'scale(1)';
                badge.style.boxShadow = '0 2px 4px rgba(102, 126, 234, 0.3)';
            });
            
            // 找到合适的位置插入
            const cardElement = element.closest('.bg-white, .rounded, .border, .shadow');
            if (cardElement) {
                // 在卡片内部添加
                const titleElement = cardElement.querySelector('h3, h2, .font-bold, .text-lg');
                if (titleElement) {
                    titleElement.appendChild(badge);
                } else {
                    element.appendChild(badge);
                }
            } else {
                // 直接在链接后添加
                element.appendChild(badge);
            }
        }
        
        updateCardCount(url, count) {
            const links = document.querySelectorAll(`a[href="${url}"]`);
            links.forEach(link => {
                const badge = link.querySelector('.reading-count');
                if (badge) {
                    badge.innerHTML = `<span class="reading-icon">👁</span> ${this.formatCount(count)}`;
                } else {
                    this.addReadingCountBadge(link, count);
                }
            });
        }
        
        formatCount(count) {
            if (count < 1000) return count.toString();
            if (count < 10000) return `${(count/1000).toFixed(1)}k`;
            return `${Math.floor(count/1000)}k`;
        }
        
        // 获取热门内容
        async getPopularContent() {
            try {
                const response = await fetch(CONFIG.apiBaseUrl + '/api/popular');
                if (response.ok) {
                    return await response.json();
                }
            } catch (error) {
                console.warn('获取热门内容失败:', error);
            }
            return [];
        }
    }
    
    // 等待DOM加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.readingTracker = new ReadingTracker();
        });
    } else {
        window.readingTracker = new ReadingTracker();
    }
    
    // 暴露API给外部使用
    window.CUHKStudyStats = {
        getPopular: () => window.readingTracker?.getPopularContent(),
        getStats: (url) => window.readingTracker?.fetchStats(url),
        track: (url, title) => window.readingTracker?.trackCardClick(url, title)
    };
    
})();