import { useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../../../shared/api/client";

import LoginHeader from "../components/LoginHeader";
import LoginFooter from "../components/LoginFooter";

import "./Register.css";


export default function Register(){

    const navigate = useNavigate();


    const [name,setName]=useState("");
    const [email,setEmail]=useState("");
    const [password,setPassword]=useState("");
    const [confirm,setConfirm]=useState("");

    const [error,setError]=useState("");
    const [success,setSuccess]=useState("");


    async function handleRegister(e){

        e.preventDefault();

        if (password.length < 8) { setError("Use a password with at least 8 characters."); return; }


        if(password !== confirm){

            setError("Passwords do not match");
            return;

        }


        try{

            await api.post(
                "/users/register",
                {
                    name,
                    email,
                    password
                }
            );


            setSuccess("Account created successfully");

            setTimeout(()=>{
                navigate("/");
            },1500);


        }catch{

            setError(
                "Registration failed"
            );

        }

    }


    return(

        <div className="register-page">


            <LoginHeader />


            <div className="register-card">


                <h1>
                    Create Account
                </h1>


                <p>
                    Start managing your AI email campaigns.
                </p>


                {
                    error && (
                        <div className="register-error">
                            {error}
                        </div>
                    )
                }

                {
                    success && (
                        <div className="success-message">
                            {success}
                        </div>
                    )
                }


                <form onSubmit={handleRegister}>


                    <input
                        type="text"
                        autoComplete="name"
                        required
                        aria-label="Full name"
                        placeholder="Full name"
                        value={name}
                        onChange={
                            e=>setName(e.target.value)
                        }
                    />


                    <input
                        type="email"
                        autoComplete="email"
                        required
                        aria-label="Email address"
                        placeholder="Email"
                        value={email}
                        onChange={
                            e=>setEmail(e.target.value)
                        }
                    />


                    <input
                        type="password"
                        autoComplete="new-password"
                        minLength={8}
                        required
                        aria-label="Password"
                        placeholder="Password"
                        value={password}
                        onChange={
                            e=>setPassword(e.target.value)
                        }
                    />


                    <input
                        type="password"
                        autoComplete="new-password"
                        minLength={8}
                        required
                        aria-label="Confirm password"
                        placeholder="Confirm password"
                        value={confirm}
                        onChange={
                            e=>setConfirm(e.target.value)
                        }
                    />


                    <button>
                        Create Account
                    </button>


                </form>


                <a
                    onClick={()=>navigate("/")}
                >
                    Already have an account? Login
                </a>


            </div>


            <LoginFooter />


        </div>

    );

}
