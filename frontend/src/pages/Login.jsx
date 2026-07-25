import Button from "../components/Button";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";


export default function Login(){

    const [email,setEmail] = useState("");
    const [password,setPassword] = useState("");

    const navigate = useNavigate();


    async function handleLogin(e){

        e.preventDefault();


        const data = new URLSearchParams();

        data.append(
            "username",
            email
        );

        data.append(
            "password",
            password
        );


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


        navigate("/dashboard");
    }


    return (
        <div>

            <h1>
                AI Email Marketing
            </h1>


            <form onSubmit={handleLogin}>

                <input
                    placeholder="Email"
                    value={email}
                    onChange={
                        e=>setEmail(e.target.value)
                    }
                />


                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={
                        e=>setPassword(e.target.value)
                    }
                />


                <Button>
                    Login
                </Button>


            </form>

        </div>
    )
}
