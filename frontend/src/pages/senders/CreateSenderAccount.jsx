import {useState} from "react";
import {useNavigate} from "react-router-dom";
import api from "../../api/client";


export default function CreateSenderAccount(){

const navigate = useNavigate();


const [form,setForm]=useState({
email:"",
display_name:"",
smtp_password:""
});


function change(e){

setForm({
...form,
[e.target.name]:e.target.value
});

}



async function submit(e){

e.preventDefault();

try{

await api.post("/sender-accounts/",form);

navigate("/senders");

}
catch(err){

console.log(err.response?.data || err);

}

}



return (

<div className="page">


<button onClick={()=>navigate("/senders")}>
← Back
</button>


<h1>
Add Sender Account
</h1>


<p className="subtitle">
Configure email sending account
</p>



<form
onSubmit={submit}
style={{
display:"grid",
gap:"18px",
maxWidth:"600px",
marginTop:"30px"
}}
>


<input
name="display_name"
placeholder="Display Name"
onChange={change}
/>


<input
name="email"
placeholder="Email Address"
type="email"
onChange={change}
/>


<input
name="smtp_password"
placeholder="SMTP Password"
type="password"
onChange={change}
/>


<button>
Create Sender
</button>


</form>


</div>

)

}
