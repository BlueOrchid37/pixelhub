// App.js
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/login";
import Wallpapers from "./pages/wallpapers";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/wallpapers" element={<Wallpapers />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
