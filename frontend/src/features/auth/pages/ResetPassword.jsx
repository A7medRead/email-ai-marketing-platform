import { useState } from "react";
import api from "../../../shared/api/client";
import "./ForgotPassword.css";

export default function ResetPassword(){

    const [password,setPassword]=useState("");
    const [confirm,setConfirm]=useState("");
    const [done,setDone]=useState(false);
    const [error,setError]=useState("");

    const token = new URLSearchParams(window.location.search).get("token");


    async function handleSubmit(e){

        e.preventDefault();

        if (!token) {
            setError("This password reset link is invalid or incomplete. Request a new link.");
            return;
        }
        if (password.length < 8) {
            setError("Use a password with at least 8 characters.");
            return;
        }
        if (password !== confirm) {
            setError("Passwords do not match.");
            return;
        }

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

                <p>Choose a new password of at least 8 characters.</p>


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
                                autoComplete="new-password"
                                required
                                value={password}
                                onChange={
                                    e=>setPassword(e.target.value)
                                }
                            />

                            <input
                                type="password"
                                placeholder="Confirm new password"
                                autoComplete="new-password"
                                required
                                value={confirm}
                                onChange={e=>setConfirm(e.target.value)}
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
