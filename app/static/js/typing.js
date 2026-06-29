document.addEventListener("DOMContentLoaded",()=>{

    const element=document.getElementById("heroTypewriter");

    if(!element) return;

    const words=[

        "backend systems",

        "web applications",

        "REST APIs",

        "Flask projects",

        "scalable software"

    ];

    let word=0;

    let letter=0;

    let deleting=false;

    function type(){

        const current=words[word];

        if(!deleting){

            element.textContent=current.substring(0,letter);

            letter++;

            if(letter>current.length){

                deleting=true;

                setTimeout(type,1200);

                return;

            }

        }

        else{

            element.textContent=current.substring(0,letter);

            letter--;

            if(letter<0){

                deleting=false;

                word=(word+1)%words.length;

                letter=0;

            }

        }

        setTimeout(type,deleting?40:80);

    }

    type();

});