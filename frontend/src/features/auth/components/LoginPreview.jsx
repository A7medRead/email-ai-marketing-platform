import "./LoginPreview.css";

export default function LoginPreview(){

    return(

        <div className="login-preview">

            <div className="preview-header">
                <h3>Campaign Performance</h3>
                <span>AI Analytics</span>
            </div>


            <div className="preview-chart">

                <div className="chart-line"></div>

            </div>


            <div className="preview-cards">

                <div>
                    <small>Emails Sent</small>
                    <strong>12,540</strong>
                </div>


                <div>
                    <small>Open Rate</small>
                    <strong>67.2%</strong>
                </div>


                <div>
                    <small>Clicks</small>
                    <strong>2,104</strong>
                </div>

            </div>


            <div className="ai-suggestion">

                <h4>
                    ✨ AI Suggestion
                </h4>

                <p>
                    Your campaign subject can improve open rates by 24%.
                </p>

                <button>
                    Apply
                </button>

            </div>


        </div>

    );

}
