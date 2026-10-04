import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { useNavigate } from "react-router-dom";

import api from "../../../shared/api/client";

import Button from "../../../shared/ui/Button";
import LoginPreview from "../components/LoginPreview";
import LoginFeatures from "../components/LoginFeatures";
import LoginFooter from "../components/LoginFooter";
import LoginHeader from "../components/LoginHeader";

import "./Login.css";


export default function Login(){

    const [email,setEmail]=useState(() => localStorage.getItem("rememberEmail") || "");
    const [password,setPassword]=useState("");
    const [error,setError]=useState("");
    const [rememberMe,setRememberMe]=useState(() => Boolean(localStorage.getItem("rememberEmail")));
    const [showPassword,setShowPassword]=useState(false);

    const navigate=useNavigate();

    async function handleLogin(e){

        e.preventDefault();

        try{

            const data=new URLSearchParams();

            data.append("username",email);
            data.append("password",password);


            const response = await api.post(
                "/users/login",
                data,
                {
                    headers:{
                        "Content-Type":
                        "application/x-www-form-urlencoded"
                    }
                }
            );


            localStorage.setItem(
                "token",
                response.data.access_token
            );


            if(rememberMe){

                localStorage.setItem(
                    "rememberEmail",
                    email
                );

            }else{

                localStorage.removeItem(
                    "rememberEmail"
                );

            }


            navigate("/dashboard");


        }catch{

            setError("Invalid email or password");

        }

    }


    return(

        <div className="login-page">

            <LoginHeader />



            <div className="login-container">

                <div className="login-card">

                    <h1>
                        Welcome <span>Back.</span>
                    </h1>

                    <p>
                        Login to manage your email campaigns.
                    </p>


                    {error && (
                        <div className="login-error">
                            {error}
                        </div>
                    )}


                    <form onSubmit={handleLogin}>


                        <div className="login-field">

                            <input
                                placeholder="Email"
                                value={email}
                                onChange={
                                    e=>setEmail(e.target.value)
                                }
                            />

                        </div>


                        <div className="login-field">

                            <input
                                type={showPassword ? "text" : "password"}
                                placeholder="Password"
                                value={password}
                                onChange={
                                    e=>setPassword(e.target.value)
                                }
                            />

                            <button
                                type="button"
                                className="password-toggle"
                                onClick={()=>setShowPassword(!showPassword)}
                            >
                                {
                                    showPassword
                                    ? <EyeOff size={18}/>
                                    : <Eye size={18}/>
                                }
                            </button>

                        </div>


                        <div className="login-options">

                            <label>
                                <input type="checkbox" checked={rememberMe} onChange={(e)=>setRememberMe(e.target.checked)}/>
                                Remember me
                            </label>

                            <a onClick={()=>navigate("/forgot-password")}>
                                Forgot password?
                            </a>

                            <a
                                onClick={()=>navigate("/register")}
                            >
                                Create new account
                            </a>

                        </div>


                        <Button className="login-btn" type="submit">
                            Login
                        </Button>


                    </form>


                </div>


                


                <div className="login-hero">

                    <LoginPreview />

                </div>
            </div>

            <LoginFeatures />

            <LoginFooter />

        </div>

    );

}
