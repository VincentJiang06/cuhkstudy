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
        
        // 让TopBar始终可见，不受滚动影响
        menuBlur.style.opacity = '1';
        console.log('TopBar set to always visible');
        
        // 可选：保留滚动效果但调整背景透明度
        let scrollHandler = function() {
            let scroll = window.pageYOffset || document.documentElement.scrollTop || 0;
            let bgOpacity = Math.min(0.15 + (scroll / 1000) * 0.1, 0.25); // 从0.15增加到0.25
            menuBlur.style.backgroundColor = `rgba(255, 255, 255, ${bgOpacity})`;
            console.log('Scroll:', scroll, 'Background opacity:', bgOpacity);
        };
        
        window.addEventListener('scroll', scrollHandler);
        console.log('Enhanced scroll effect added');
        
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