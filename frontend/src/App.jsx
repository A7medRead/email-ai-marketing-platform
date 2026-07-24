import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Campaigns from "./pages/campaigns/Campaigns";
import CreateCampaign from "./pages/campaigns/CreateCampaign";
import Analytics from "./pages/analytics/Analytics";
import CampaignPerformance from "./pages/campaigns/CampaignPerformance";
import CampaignDetails from "./pages/campaigns/CampaignDetails";
import Layout from "./components/Layout";


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


</Route>


</Routes>

</BrowserRouter>

)

}

export default App;
