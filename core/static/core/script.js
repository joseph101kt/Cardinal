document.addEventListener("DOMContentLoaded", function () {
    const post_divs = document.querySelectorAll('.post_div')
    post_divs.forEach(post_div => {

        const post_id = post_div.dataset.id;

        const like_btn = post_div.querySelector('.like_btn');
        const update_like_url = like_btn.dataset.url;

        const post_content = post_div.querySelector('.post_content');

        const edit_post_btn = post_div.querySelector('.edit_post_btn');        

        const edit_post_content = post_div.querySelector('.edit_post_content');
        const save_edited_post_content_btn = post_div.querySelector('.save_edited_post_content_btn');

        handle_edit_post()

        

        like_btn.addEventListener('click', () => {
            update_like_state()
        })


        function show_post_content_edit() {
            // hide the post_content paragraph
            post_content.style.display = "none";
            edit_post_btn.style.display = "none";
            // show the edit text_area and btn
            edit_post_content.style.display = "block";
            edit_post_content.value = post_content.innerHTML 
            save_edited_post_content_btn.style.display = "block";
        }

        function handle_edit_post() {
                // hide the edit text_area and btn
            edit_post_content.style.display = "none";
            save_edited_post_content_btn.style.display = "none";

            if (edit_post_btn) {
                edit_post_btn.addEventListener('click', () => {
                    show_post_content_edit()
                });
            }


            if (save_edited_post_content_btn) {

                save_edited_post_content_btn.addEventListener('click', () => {
                    const new_content =  edit_post_content.value;

                    fetch('/update_post_content', {
                        method: "PUT",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            content: new_content,
                            post_id: post_id
                        })
                    })
                    .then(response => {
                        return response.json();
                    })
                    .then(data => {


                        post_content.innerHTML = data.content;
                        post_content.style.display = "block";
                        edit_post_btn.style.display = "block";

                        // hide the edit text_area and btn
                        edit_post_content.style.display = "none";
                        save_edited_post_content_btn.style.display = "none";
                    })
                    .catch(error => {
                        console.error("faild to update the post content");
                    });
                });
            }
        }

        function update_like_state () {
            console.log(post_id),
            fetch(update_like_url,{
                method: "PUT",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ post_id: post_id })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Server error");
                }
                return response.json()
            })
            .then(data => {
                console.log(data)
                like_btn.innerHTML = "&#x2764;&#xFE0F;" + data.like_count
            })
            .catch(error => {
                console.error("Error while updating Like state:", error);
                alert("Something went wrong: Error while updating Like state.");
            });
        }


    });
});


function update_like_state () {
    fetch("{% url 'update_like_state' %}",{
        method: "PUT",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ post_id: post_id })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Server error");
        }
        return response.json()
    })
    .then(data => {
        document.querySelector('#like_btn').innerHTML = "Like count: " + data.like_count
    })
    .catch(error => {
        console.error("Error while updating Like state:", error);
        alert("Something went wrong: Error while updating Like state.");
    });
}
