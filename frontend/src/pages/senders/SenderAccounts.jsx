import "./SenderAccounts.css";
import { useEffect,useState,useRef } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/client";
import Button from "../../components/Button";
import Card from "../../components/Card";
import Loading from "../../components/Loading";
import EmptyState from "../../components/EmptyState";


export default function SenderAccounts(){

const [senders,setSenders]=useState([]);
const [search,setSearch]=useState("");
const [status,setStatus]=useState("");
const [page,setPage]=useState(1);
const [hasMore,setHasMore]=useState(true);
const [pageLoading,setPageLoading]=useState(true);
const [message,setMessage]=useState("");
const fileInput=useRef(null);
const navigate=useNavigate();


async function importSenders(e){

const file=e.target.files[0];

if(!file)
return;


const formData=new FormData();

formData.append(
"file",
file
);


try{

const res=await api.post(
"/sender-accounts/import",
formData,
{
headers:{
"Content-Type":"multipart/form-data"
}
}
);


setMessage(
`Imported ${res.data.imported} sender accounts`
);


load();


}
catch(err){

console.log(err);

setMessage(
"Import failed"
);

}

}


async function exportSenders(){

try{

const res = await api.get(
"/sender-accounts/export",
{
responseType:"blob"
}
);


const url = window.URL.createObjectURL(
new Blob([res.data])
);


const link=document.createElement("a");

link.href=url;

link.download="sender_accounts.csv";

document.body.appendChild(link);

link.click();

link.remove();


}
catch(err){

console.log(err);

}

}


async function load(){

const res = await api.get("/sender-accounts/",{
params:{
page,
limit:10,
search,
status
}
});

setSenders(res.data);

setHasMore(res.data.length === 10);

setPageLoading(false);

}


useEffect(()=>{

load();

},[page,search,status]);



async function remove(id){

const ok = window.confirm(
"Are you sure you want to delete this sender account?"
);

if(!ok) return;

await api.delete(`/sender-accounts/${id}`);

load();

}



async function verify(id){

await api.post(`/sender-accounts/${id}/verify`);

load();

}



async function sendTest(id){

const email = window.prompt(
"Enter test email address"
);

if(!email) return;


await api.post(
`/sender-accounts/${id}/send-test`,
{
recipient_email:email
}
);

alert("Test email sent");

}



if(pageLoading)
return <Loading />;


return (

<div className="page">


<div className="contacts-header">

<div>

<h1>
Sender Accounts
</h1>

<p className="subtitle">
Manage your email sending accounts
</p>

</div>


<input
type="file"
accept=".csv"
ref={fileInput}
style={{display:"none"}}
onChange={importSenders}
/>


<Button
variant="secondary"
onClick={exportSenders}
>
📤 Export CSV
</Button>


<Button
variant="secondary"
onClick={()=>fileInput.current.click()}
>
📥 Import CSV
</Button>


<Button
onClick={()=>navigate("/senders/create")}
>
+ Add Sender
</Button>


</div>



<input
placeholder="Search sender accounts..."
value={search}
onChange={(e)=>{
setPage(1);
setSearch(e.target.value);
}}
className="contact-search"
/>


<select
value={status}
onChange={(e)=>{
setPage(1);
setStatus(e.target.value);
}}
>

<option value="">
All Status
</option>

<option value="PENDING">
Pending
</option>

<option value="VERIFIED">
Verified
</option>

<option value="FAILED">
Failed
</option>

</select>


<div className="senders-cards">


{
senders.length === 0
?
<EmptyState
title="No sender accounts found"
message="Add a sender account to start sending emails"
/>
:
senders.map(sender=>(

<Card className="senders-card" key={sender.id}>


<div className="senders-avatar">
✉️
</div>


<h2>
{sender.name}
</h2>


<p>
{sender.email}
</p>


<p>
Provider: {sender.provider}
</p>


<span>
Status: {sender.status}
</span>



<div className="senders-actions">


<Button
variant="secondary"
onClick={()=>navigate(`/senders/${sender.id}/edit`)}
>
✎ Edit
</Button>


<Button
onClick={()=>verify(sender.id)}
>
✓ Verify
</Button>


<Button
variant="secondary"
onClick={()=>sendTest(sender.id)}
>
📨 Test
</Button>


<Button
variant="danger"
onClick={()=>remove(sender.id)}
>
🗑 Delete
</Button>


</div>


</Card>

))
}


</div>




<div className="contacts-pagination">

<Button
variant="secondary"
disabled={page===1}
onClick={()=>setPage(page-1)}
>
← Previous
</Button>


<span>
Page {page}
</span>


<Button
variant="secondary"
disabled={!hasMore}
onClick={()=>setPage(page+1)}
>
Next →
</Button>


</div>



</div>

)

}
