import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Campaigns from "./pages/campaigns/Campaigns";
import CreateCampaign from "./pages/campaigns/CreateCampaign";
import Analytics from "./pages/analytics/Analytics";
import CampaignPerformance from "./pages/campaigns/CampaignPerformance";
import CampaignDetails from "./pages/campaigns/CampaignDetails";
import EditCampaign from "./pages/campaigns/EditCampaign";

import Templates from "./pages/templates/Templates";
import CreateTemplate from "./pages/templates/CreateTemplate";
import EditTemplate from "./pages/templates/EditTemplate";
import Emails from "./pages/emails/Emails";
import CreateEmail from "./pages/emails/CreateEmail";
import EmailDetails from "./pages/emails/EmailDetails";
import Layout from "./components/Layout";
import SenderAccounts from "./pages/senders/SenderAccounts";
import CreateSenderAccount from "./pages/senders/CreateSenderAccount";
import EditSenderAccount from "./pages/senders/EditSenderAccount";
import Contacts from "./pages/contacts/Contacts";
import CreateContact from "./pages/contacts/CreateContact";
import ContactDetails from "./pages/contacts/ContactDetails";
import EditContact from "./pages/contacts/EditContact";
import ContactLists from "./pages/contactlists/ContactLists";
import CreateContactList from "./pages/contactlists/CreateContactList";
import ManageContactList from "./pages/contactlists/ManageContactList";



function App(){

return (

<BrowserRouter>

<Routes>


<Route
path="/"
element={<Login />}
/>


<Route element={<Layout />}>

<Route
path="/dashboard"
element={<Dashboard />}
/>


<Route
path="/campaigns"
element={<Campaigns />}
/>

<Route
path="/campaigns/create"
element={<CreateCampaign />}
/>

<Route
path="/campaigns/:id/analytics"
element={<Analytics />}
/>

<Route
path="/campaigns/:id/performance"
element={<CampaignPerformance />}
/>

<Route
path="/campaigns/:id/details"
element={<CampaignDetails />}
/>


<Route
path="/campaigns/:id/edit"
element={<EditCampaign />}
/>

<Route path="/templates" element={<Templates />} />
<Route path="/templates/create" element={<CreateTemplate />} />
<Route path="/templates/:id/edit" element={<EditTemplate />} />

<Route path="/emails" element={<Emails />} />
<Route path="/emails/create" element={<CreateEmail />} />
<Route path="/emails/:id" element={<EmailDetails />} />


<Route path="/senders" element={<SenderAccounts />} />
<Route path="/senders/create" element={<CreateSenderAccount />} />
<Route path="/senders/:id/edit" element={<EditSenderAccount />} />

<Route path="/contacts" element={<Contacts />} />
<Route path="/contacts/create" element={<CreateContact />} />
<Route path="/contacts/:id/edit" element={<EditContact />} />
<Route path="/contacts/:id" element={<ContactDetails />} />
<Route path="/contact-lists/:id/manage" element={<ManageContactList />} />


<Route path="/contact-lists" element={<ContactLists />} />
<Route path="/contact-lists/create" element={<CreateContactList />} />

</Route>


</Routes>

</BrowserRouter>

)

}

export default App;
