import { useEffect, useState } from "react";
import api from "../../api/client";


export default function SenderAccounts(){

const [senders,setSenders] = useState([]);


useEffect(()=>{

api.get("/sender-accounts/")
.then(res=>{
setSenders(res.data);
})
.catch(err=>{
console.log(err);
});

},[]);



return (

<div className="sender-page">


<div className="page-header">

<div>

<h1>
Sender Accounts
</h1>

<p>
Manage your email sending accounts
</p>

</div>


</div>



<div className="sender-grid">


{
senders.map(sender=>(


<div className="sender-card" key={sender.id}>


<div className="sender-icon">
✉️
</div>


<h2>
{sender.name}
</h2>


<div className="sender-email">
{sender.email}
</div>



<div className="sender-info">


<p>
Provider
<strong>
{sender.provider}
</strong>
</p>



<p>
Status

<span className={`status ${sender.status.toLowerCase()}`}>
{sender.status}
</span>

</p>


</div>



</div>


))
}


</div>


</div>

)

}
