import { useEffect, useState } from "react";
import { apiFetch } from "../services/api";

function Wallpapers() {
  const [wallpapers, setWallpapers] = useState([]);

  useEffect(() => {
    apiFetch("/api/pixelhub/wallpapers")
      .then((res) => res.json())
      .then((data) => setWallpapers(data));
  }, []);

  return (
    <div>
      <h1>PixelHub Wallpapers</h1>

      <div className="grid">
        {wallpapers.map((w) => (
          <img key={w.id} src={w.image_url} alt="wallpaper" />
        ))}
      </div>
    </div>
  );
}

export default Wallpapers;
