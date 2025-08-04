// 调试TopBar模糊效果
console.log('Debug blur script loaded');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, checking blur elements...');
    
    const menuBlur = document.getElementById('menu-blur');
    const backgroundBlur = document.getElementById('background-blur');
    
    if (menuBlur) {
        console.log('menu-blur element found:', menuBlur);
        console.log('menu-blur classes:', menuBlur.className);
        console.log('menu-blur style:', menuBlur.style.cssText);
        
        // 移除调试类，使用正常效果
        // menuBlur.classList.add('debug-visible');
        
        // 手动实现滚动监听以测试
        let scrollHandler = function() {
            let scroll = window.pageYOffset || document.documentElement.scrollTop || 0;
            let opacity = Math.min(scroll / 300, 1);
            menuBlur.style.opacity = opacity;
            console.log('Scroll:', scroll, 'Opacity:', opacity);
        };
        
        window.addEventListener('scroll', scrollHandler);
        console.log('Custom scroll listener added');
        
        // 测试立即设置
        setTimeout(() => {
            menuBlur.style.opacity = '0.8';
            console.log('Test opacity set to 0.8');
        }, 1000);
        
    } else {
        console.error('menu-blur element NOT found!');
    }
    
    if (backgroundBlur) {
        console.log('background-blur element found:', backgroundBlur);
    } else {
        console.error('background-blur element NOT found!');
    }
    
    // 检查localStorage设置
    const a11ySettings = JSON.parse(localStorage.getItem('a11ySettings') || '{}');
    console.log('A11y settings:', a11ySettings);
    
    // 列出所有script标签
    const scripts = document.querySelectorAll('script[data-target-id]');
    console.log('Found scripts with data-target-id:', scripts.length);
    scripts.forEach((script, index) => {
        console.log(`Script ${index}:`, script.getAttribute('data-target-id'), script.src);
    });
});