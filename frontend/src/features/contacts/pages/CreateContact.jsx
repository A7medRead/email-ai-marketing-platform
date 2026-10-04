import Button from "../../../shared/ui/Button";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../../shared/api/client";

export default function CreateContact(){

const navigate = useNavigate();

const [form,setForm]=useState({
first_name:"",
last_name:"",
email:"",
company:"",
phone:"",
position:""
});


function handle(e){

setForm({
...form,
[e.target.name]:e.target.value
});

}



async function submit(e){

e.preventDefault();

try{

await api.post("/contacts/",form);

navigate("/contacts");

}
catch(err){

console.log(err.response?.data || err);

}

}



return (

<div className="page">


<Button
variant="secondary"
onClick={()=>navigate("/contacts")}
>
← Back
</Button>

<h1>
Add Contact
</h1>

<p className="subtitle">
Create a new customer contact
</p>



<div className="form-card">


<form onSubmit={submit} className="form-stack">


<label className="form-field">First Name<input id="first-name" name="first_name" onChange={handle} /></label>


<label className="form-field">Last Name<input id="last-name" name="last_name" onChange={handle} /></label>


<label className="form-field">Email Address<input id="contact-email" name="email" type="email" onChange={handle} /></label>


<label className="form-field">Company<input id="company" name="company" onChange={handle} /></label>


<label className="form-field">Phone Number<input id="phone" name="phone" onChange={handle} /></label>


<label className="form-field">Job Position<input id="position" name="position" onChange={handle} /></label>



<Button
type="submit"
>
Create Contact
</Button>


</form>


</div>


</div>

)

}
