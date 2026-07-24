import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/client";

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


<button onClick={()=>navigate("/contacts")}>← Back</button>

<h1>
Add Contact
</h1>

<p className="subtitle">
Create a new customer contact
</p>



<div style={{
maxWidth:"600px",
marginTop:"40px",
background:"#16171d",
border:"1px solid #2e303a",
padding:"30px",
borderRadius:"16px"
}}>


<form
onSubmit={submit}
style={{
display:"grid",
gap:"18px"
}}
>


<input
name="first_name"
placeholder="First Name"
onChange={handle}
/>


<input
name="last_name"
placeholder="Last Name"
onChange={handle}
/>


<input
name="email"
placeholder="Email Address"
type="email"
onChange={handle}
/>


<input
name="company"
placeholder="Company"
onChange={handle}
/>


<input
name="phone"
placeholder="Phone Number"
onChange={handle}
/>


<input
name="position"
placeholder="Job Position"
onChange={handle}
/>



<button
style={{
marginTop:"10px"
}}
>
Create Contact
</button>


</form>


</div>


</div>

)

}
