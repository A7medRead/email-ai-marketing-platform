import "./Emails.css";

import {useEffect,useState} from "react";
import {useParams,Link} from "react-router-dom";
import api from "../../api/client";

export default function EmailDetails(){

const {id}=useParams();
const [email,setEmail]=useState(null);


useEffect(()=>{

api.get(`/email/${id}`)
.then(res=>{
setEmail(res.data);
})
.catch(err=>{
console.log(err);
});

},[id]);


if(!email)
return <h1>Loading...</h1>;


return (

<div className="email-details-page">

<Link to="/emails">
← Back to Emails
</Link>

<h1>Email Details</h1>

<hr/>


<h2>
{email.subject}
</h2>


<p>
<b>ID:</b> {email.id}
</p>


<p>
<b>Purpose:</b> {email.purpose}
</p>


<p>
<b>Tone:</b> {email.tone}
</p>


<p>
<b>Language:</b> {email.language}
</p>


<p>
<b>Created:</b> {email.created_at}
</p>


<hr/>


<h3>Description</h3>

<p>
{email.description}
</p>


<hr/>


<h3>Email Body</h3>

<pre style={{
whiteSpace:"pre-wrap",
fontFamily:"inherit"
}}>
{email.body}
</pre>


</div>

)

}
