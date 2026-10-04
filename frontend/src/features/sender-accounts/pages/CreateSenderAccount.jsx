import Button from "../../../shared/ui/Button";
import {useState} from "react";
import {useNavigate} from "react-router-dom";
import api from "../../../shared/api/client";


export default function CreateSenderAccount(){

const navigate = useNavigate();


const [form,setForm]=useState({
email:"",
display_name:"",
smtp_password:""
});
const [error,setError]=useState("");


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
setError("Could not create the sender account. Check the details and try again.");

}

}



return (

<div className="page">


<Button
variant="secondary"
onClick={()=>navigate("/senders")}
>
← Back
</Button>


<h1>
Add Sender Account
</h1>


<p className="subtitle">
Configure email sending account
</p>



<div className="form-card"><form onSubmit={submit} className="form-stack">


<label className="form-field">Display Name<input required name="display_name" value={form.display_name} onChange={change} /></label>


<label className="form-field">Email Address<input required type="email" autoComplete="email" name="email" value={form.email} onChange={change} /></label>


<label className="form-field">SMTP Password<input required type="password" autoComplete="new-password" name="smtp_password" value={form.smtp_password} onChange={change} /></label>

{error && <p role="alert" className="form-error">{error}</p>}


<Button type="submit">
Create Sender
</Button>


</form></div>


</div>

)

}
