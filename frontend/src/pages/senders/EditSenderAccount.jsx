import {useEffect,useState} from "react";
import {useParams,useNavigate} from "react-router-dom";
import api from "../../api/client";


export default function EditSenderAccount(){

const {id}=useParams();
const navigate=useNavigate();


const [form,setForm]=useState({
email:"",
display_name:"",
smtp_password:""
});



useEffect(()=>{

api.get("/sender-accounts/")
.then(res=>{

const sender=res.data.find(
x=>String(x.id)===String(id)
);

if(sender){

setForm({
email:sender.email,
display_name:sender.name,
smtp_password:""
});

}

});

},[id]);



function change(e){

setForm({
...form,
[e.target.name]:e.target.value
});

}



async function submit(e){

e.preventDefault();

await api.put(
`/sender-accounts/${id}`,
form
);

navigate("/senders");

}



return (

<div className="page">


<button onClick={()=>navigate("/senders")}>
← Back
</button>


<h1>
Edit Sender Account
</h1>


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
value={form.display_name}
placeholder="Display Name"
onChange={change}
/>


<input
name="email"
value={form.email}
placeholder="Email"
onChange={change}
/>


<input
name="smtp_password"
type="password"
placeholder="New SMTP Password (optional)"
onChange={change}
/>


<button>
Save Changes
</button>


</form>


</div>

)

}
