import "./LoginFeatures.css";

export default function LoginFeatures(){

    const features=[
        {
            icon:"✨",
            title:"AI Content Generation",
            text:"Create engaging email content powered by artificial intelligence."
        },
        {
            icon:"🚀",
            title:"Smart Campaigns",
            text:"Automate campaigns and reach your audience faster."
        },
        {
            icon:"📊",
            title:"Real-time Analytics",
            text:"Track performance and optimize your marketing results."
        },
        {
            icon:"👥",
            title:"Audience Management",
            text:"Manage contacts and create powerful segments."
        }
    ];


    return(

        <div className="login-features">

            {
                features.map((item,index)=>(

                    <div className="feature-card" key={index}>

                        <div className="feature-icon">
                            {item.icon}
                        </div>

                        <h3>
                            {item.title}
                        </h3>

                        <p>
                            {item.text}
                        </p>

                    </div>

                ))
            }

        </div>

    );

}
