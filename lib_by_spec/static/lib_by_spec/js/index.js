let CSRFTOKEN = getCookie("csrftoken"); 

function getCookie(c_name) {
    if (document.cookie.length > 0) {
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1) {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) {
                c_end = document.cookie.length;
            }
            return unescape(document.cookie.substring(c_start, c_end));
        }
    }
    return "";
}

class Book {
    constructor(node) {
        this.node = node
        
        this.favoriteBtn = this.node.querySelector("button")
        if (this.favoriteBtn !== null) {
            
            this.favoriteBtn_blocked = false
            this.favoriteBtn.addEventListener('click', () => {
                let url = this.favoriteBtn.getAttribute('data-url')
                this.addToFavorite(url).then(() => {
                    this.favoriteBtn_blocked = false
                    console.log('unlocked')
                })
                .catch(() => {
                    console.log("already used")
                })
                
            })
        }
        
    }

    async addToFavorite(url) {
        if(this.favoriteBtn_blocked == true) {
            throw Error("Ожидание ответа сервера...")
        }
        this.favoriteBtn_blocked = true 

        try {
            let response = await fetch("http://127.0.0.1:8000"+url, 
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': CSRFTOKEN,
                    },
                    body: JSON.stringify({
                        'text': 'test_data',
                    }),
                }
            );

            let result = await response.json();
            
            if(result['ok'] == false) {
                return "Unexpected error"
            }
             
            if(result['success'] == false) {
                console.log(result['err_msg'])
                return result['err_msg']
            }

            console.log(result)
            this.favoriteBtn
            if(result['added'] == true) 
                this.favoriteBtn.classList.add('active') 
            else 
                this.favoriteBtn.classList.remove('active')
            
        }
        catch (err) {
            console.log(err)
            console.log("Catched at get");
            return ({"ok": false, "result": {status: "error", message: "Unexpected server error"}});
        }

    }
}

books_nodes = document.querySelectorAll(".book-list__item");

for(let i=0;i < books_nodes.length;i++) {
    new Book(books_nodes[i])
}