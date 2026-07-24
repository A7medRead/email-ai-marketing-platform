
import {useState} from "react";
import api from "../../api/client";

export default function CreateEmail(){

const [form,setForm]=useState({
purpose:"",
description:"",
tone:"Professional",
language:"English"
});

const [result,setResult]=useState(null);


function change(e){
setForm({
...form,
[e.target.name]:e.target.value
});
}


function submit(){

api.post("/email/generate",form)
.then(res=>{
setResult(res.data);
})
.catch(err=>{
console.log(err);
});

}


return (

<div>

<h1>Create Email</h1>


<input
name="purpose"
placeholder="Purpose"
onChange={change}
/>


<br/>


<textarea
name="description"
placeholder="Description"
onChange={change}
/>


<br/>


<button onClick={submit}>
Generate
</button>


{
result &&
<div>

<h3>{result.subject}</h3>

<p>{result.body}</p>

</div>
}


</div>

)

}
