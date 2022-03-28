import React, { useState, useEffect } from "react";

const Home = () => {
    const [original, setOriginal] = useState([])
    const [translation, setTranslation] = useState([])

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
            .then(res => res.json())
            .then(resJson => {
                console.log(resJson)
                document.getElementById("result-image").src = resJson["data_uri"];
                setOriginal(resJson["original_text"])
                setTranslation(resJson["translated_text"])
            })
        }
        reader.readAsDataURL(file);
    }

    const TEXT_MAPPER = (props) => {
        console.log(props.text)
        return (
            <div className={props.lang_map}>
                {props.text}
            </div>
        )
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
                <div className="text-container">
                    <div className="original-container">
                        <div className="original-text">
                            Original
                        </div>
                        {
                            original.map( (text) => 
                            {
                                return <TEXT_MAPPER text={text} lang_map={"original-text"}/>
                            })
                        }
                    </div>
                    <div className="translation-container">
                        <div className="translated-text">
                            Translation
                        </div>
                        {
                            translation.map( (text) => 
                            {
                                return <TEXT_MAPPER text={text} lang_map={"translated-text"}/>
                            })
                        }
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Home