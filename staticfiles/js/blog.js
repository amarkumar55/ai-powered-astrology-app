document.addEventListener("DOMContentLoaded", function () {
    console.log("💡 blog.js loaded");

    const quill = new Quill('#editor', {
        theme: 'snow',
        modules: {
            toolbar: [
                [{ header: [1, 2, 3, false] }],
                ['bold', 'italic', 'underline'],
                [{ list: 'ordered' }, { list: 'bullet' }],
                ['link'],
                ['clean']
            ]
        }
    });

    // Load initial content
    const contentDiv = document.getElementById("post_data");
    if (contentDiv) {
        const content = contentDiv.innerHTML.trim();  // Notice: innerHTML, not textContent
        quill.root.innerHTML = content;
    }

    // On form submit, extract content using Quill API
    const form = document.getElementById("blog_form");
    const hiddenInput = document.getElementById("content");

    form.addEventListener("submit", function () {
        const contentHTML = quill.getSemanticHTML();  // ✅ Important change for Quill v2
        hiddenInput.value = contentHTML;
        console.log("📝 Submitting content:", contentHTML);
    });
});
