import { useState } from "react";
import api from "../../../shared/api/client";
import "./ForgotPassword.css";

export default function ForgotPassword(){

    const [email,setEmail]=useState("");
    const [sent,setSent]=useState(false);
    const [error,setError]=useState("");


    async function handleSubmit(e){

        e.preventDefault();

        try{

            await api.post(
                "/users/forgot-password",
                {
                    email
                }
            );


            setSent(true);


        }catch{

            setError("Unable to process the request. Please try again later.");

        }

    }


    return(

        <div className="forgot-page">


            <div className="forgot-card">

                <h1>
                    Reset Password
                </h1>


                <p>
                    Enter your email and we'll send you a reset link.
                </p>


                {
                    error && (
                        <div className="login-error">
                            {error}
                        </div>
                    )
                }


                {
                    sent ? (

                        <div className="success-message">

                            If an account matches that address, a reset link will be sent.

                        </div>


                    ) : (

                        <form onSubmit={handleSubmit}>


                            <input
                                placeholder="Email address"
                                value={email}
                                onChange={
                                    e=>setEmail(e.target.value)
                                }
                            />


                            <button>
                                Send Reset Link
                            </button>


                        </form>

                    )
                }


                <a
                    className="back-login"
                    href="/"
                >
                    Back to Login
                </a>


            </div>


        </div>

    );

}
