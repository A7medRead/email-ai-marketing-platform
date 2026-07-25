import Button from "../../components/Button";
import {useEffect,useState} from "react";
import {useParams,useNavigate} from "react-router-dom";
import api from "../../api/client";

export default function EditContact(){

const {id}=useParams();
const navigate=useNavigate();

const [form,setForm]=useState({
first_name:"",
last_name:"",
email:"",
company:"",
phone:"",
position:""
});


useEffect(()=>{

api.get(`/contacts/${id}`)
.then(res=>{
setForm(res.data);
});

},[id]);


function change(e){

setForm({
...form,
[e.target.name]:e.target.value
});

}


async function save(){

await api.put(`/contacts/${id}`,form);

navigate(`/contacts/${id}`);

}


return (

<div>

<Button
variant="secondary"
onClick={()=>navigate(`/contacts/${id}`)}
>
← Back
</Button>

<h1>Edit Contact</h1>


<div className="card"
style={{maxWidth:"500px"}}>

{[
"first_name",
"last_name",
"email",
"company",
"phone",
"position"
].map(key=>(

<input
key={key}
name={key}
value={form[key] || ""}
placeholder={key}
onChange={change}
style={{
display:"block",
width:"100%",
margin:"10px 0"
}}
/>

))}


<Button
onClick={save}
>
Save Changes
</Button>


</div>

</div>

)

}
