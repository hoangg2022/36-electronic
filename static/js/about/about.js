const loadComponent = async (url, elementId, errorElementId) => {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Không thể tải ${url}`);
        const data = await response.text();
        const element = document.getElementById(elementId);
        if (!element) throw new Error(`Không tìm thấy phần tử với ID: ${elementId}`);
        
        element.innerHTML = data;
        
        // Xử lý các script trong component
        const scripts = element.querySelectorAll('script');
        scripts.forEach(script => {
            const newScript = document.createElement('script');
            newScript.textContent = script.textContent;
            document.body.appendChild(newScript);
        });
    } catch (error) {
        console.error(`Error loading ${url}:`, error);
        const errorElement = document.getElementById(errorElementId);
        if (errorElement) errorElement.style.display = 'block';
    }
};

Promise.all([
    loadComponent('header.html', 'header', 'header-error'),
    loadComponent('footer.html', 'footer', 'footer-error')
])
.then(() => {
    console.log('Header and footer loaded successfully');
})
.catch(error => {
    console.error('One or more components failed to load:', error);
});