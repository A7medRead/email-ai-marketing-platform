import { useState } from "react";
import api from "../../../shared/api/client";

export default function ResetPassword(){

    const [password,setPassword]=useState("");
    const [done,setDone]=useState(false);
    const [error,setError]=useState("");

    const token = new URLSearchParams(window.location.search).get("token");


    async function handleSubmit(e){

        e.preventDefault();

        try{

            await api.post(
                "/users/reset-password",
                {
                    token,
                    new_password: password
                }
            );


            setDone(true);


        }catch{

            setError(
                "Invalid or expired token"
            );

        }

    }


    return (

        <div className="forgot-page">

            <div className="forgot-card">

                <h1>
                    New Password
                </h1>


                {
                    error && 
                    <div className="login-error">
                        {error}
                    </div>
                }


                {
                    done ? (

                        <div className="success-message">
                            Password updated successfully
                        </div>

                    ) : (

                        <form onSubmit={handleSubmit}>


                            <input
                                type="password"
                                placeholder="New password"
                                value={password}
                                onChange={
                                    e=>setPassword(e.target.value)
                                }
                            />


                            <button>
                                Update Password
                            </button>


                        </form>

                    )
                }


            </div>

        </div>

    );

}
