import React, { useState, useEffect } from "react";

const Home = () => {
    
    const LOG_IMG = (image) => {
        const file = image[0]

        const reader = new FileReader();
        reader.onloadend = function() {
            const data_uri = reader.result

            fetch("/imagetranslate", {
                method: "POST",
                body: JSON.stringify({
                    'data_uri': data_uri,
                }),
            })
            .then(res=>(res.json()))
            .then(resJson => {
                let canvas = document.getElementById("result-image");
                let img = new Image()

                console.log(resJson)

                document.getElementById("result-image").src = resJson["new_img"];
            })
        }
        reader.readAsDataURL(file);
    }


    return (
        <div>
            <div className="container">
                <div className="title">
                    Vision
                </div>
                <div>
                    <img src="" id="result-image" className="image"/>
                </div>
                <div>
                    <label for="img-upload" className="upload">
                        Upload image
                    </label>
                    <input id="img-upload" type="file" accept="image/*" onChange={(e) => {
                        LOG_IMG(e.target.files)
                    }}/>
                </div>
            </div>
        </div>
    )
}

export default Home